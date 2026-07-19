import httpx
import logging
import asyncio
import time
from typing import Dict, Any, Optional, AsyncIterator, Callable, List, Set, Awaitable
from pydantic import BaseModel, Field
from core.transport.exceptions import (
    TransportError,
    TransportTimeoutError,
    TransportNetworkError,
    TransportHTTPError,
    TransportRateLimitError,
    TransportUnauthorizedError,
    TransportForbiddenError,
)

logger = logging.getLogger(__name__)

# Request and Response Middleware signatures
RequestMiddleware = Callable[[httpx.Request], Awaitable[httpx.Request]]
ResponseMiddleware = Callable[[httpx.Response], Awaitable[httpx.Response]]


class TimeoutPolicy(BaseModel):
    """Configuration timeouts policy for network requests."""

    connect: float = Field(default=5.0, description="Connect timeout in seconds")
    read: float = Field(default=30.0, description="Read timeout in seconds")
    write: float = Field(default=10.0, description="Write timeout in seconds")
    pool: float = Field(default=5.0, description="Pool timeout in seconds")


class RetryPolicy(BaseModel):
    """Re-execution rules for transient network and status code failures."""

    max_retries: int = Field(default=3, description="Maximum execution attempts")
    backoff_factor: float = Field(
        default=0.5, description="Backoff factor for exponential wait duration"
    )
    status_codes: Set[int] = Field(
        default_factory=lambda: {429, 500, 502, 503, 504},
        description="HTTP status codes that trigger a retry",
    )
    retry_on_timeouts: bool = Field(
        default=True, description="Should retries execute on read/connect timeouts?"
    )


class HTTPClientFactory:
    """Manages the lifecycle and pooling configuration of a shared httpx.AsyncClient."""

    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(
        cls,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
    ) -> httpx.AsyncClient:
        """Construct or retrieve the singleton connection pool client."""
        if cls._client is None or cls._client.is_closed:
            limits = httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=max_keepalive_connections,
                keepalive_expiry=keepalive_expiry,
            )
            cls._client = httpx.AsyncClient(limits=limits)
            logger.info(
                f"Constructed singleton httpx.AsyncClient (max_conns={max_connections})"
            )
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        """Shutdown client and close active pooled socket connections."""
        if cls._client is not None and not cls._client.is_closed:
            logger.info("Closing singleton httpx.AsyncClient pool...")
            await cls._client.aclose()
            cls._client = None


class AsyncHTTPTransport:
    """A provider-agnostic HTTP client wrapper supporting retries, timeouts, and middleware pipelines."""

    def __init__(
        self,
        client: httpx.AsyncClient,
        timeout_policy: Optional[TimeoutPolicy] = None,
        retry_policy: Optional[RetryPolicy] = None,
        request_middlewares: Optional[List[RequestMiddleware]] = None,
        response_middlewares: Optional[List[ResponseMiddleware]] = None,
        metrics_hook: Optional[Callable[[str, float, bool], None]] = None,
    ) -> None:
        self.client = client
        self.timeout_policy = timeout_policy or TimeoutPolicy()
        self.retry_policy = retry_policy or RetryPolicy()
        self.request_middlewares = request_middlewares or []
        self.response_middlewares = response_middlewares or []
        self.metrics_hook = metrics_hook

    async def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        content: Optional[Any] = None,
        auth_hook: Optional[Callable[[Dict[str, str]], None]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Execute a standard HTTP request with retries, timeouts, and error handling."""
        headers_dict = dict(headers) if headers else {}
        if auth_hook:
            auth_hook(headers_dict)

        timeout = httpx.Timeout(
            connect=self.timeout_policy.connect,
            read=self.timeout_policy.read,
            write=self.timeout_policy.write,
            pool=self.timeout_policy.pool,
        )

        request = self.client.build_request(
            method=method,
            url=url,
            headers=headers_dict,
            json=json,
            params=params,
            content=content,
            timeout=timeout,
            **kwargs,
        )

        # Execute request middleware chain
        for middleware in self.request_middlewares:
            request = await middleware(request)

        retries = 0
        while True:
            start_time = time.perf_counter()
            success = False
            response = None
            try:
                logger.debug(
                    f"Sending HTTP {method} request to {url} (attempt {retries + 1})"
                )
                response = await self.client.send(request)
                response.raise_for_status()

                # Execute response middleware chain
                for resp_middleware in self.response_middlewares:
                    response = await resp_middleware(response)

                success = True
                return response

            except httpx.TimeoutException as e:
                logger.warning(
                    f"Timeout occurred on request to {url} (attempt {retries + 1}): {e}"
                )
                if (
                    self.retry_policy.retry_on_timeouts
                    and retries < self.retry_policy.max_retries
                ):
                    retries += 1
                    await self._sleep_backoff(retries)
                    continue
                raise TransportTimeoutError(
                    f"Request timed out after {retries} retries: {str(e)}"
                ) from e

            except httpx.NetworkError as e:
                logger.warning(
                    f"Network error occurred on request to {url} (attempt {retries + 1}): {e}"
                )
                if retries < self.retry_policy.max_retries:
                    retries += 1
                    await self._sleep_backoff(retries)
                    continue
                raise TransportNetworkError(
                    f"Network failure after {retries} retries: {str(e)}"
                ) from e

            except httpx.HTTPStatusError as e:
                response = e.response
                status_code = response.status_code
                logger.error(
                    f"HTTP response error {status_code} from {url} (attempt {retries + 1})"
                )

                if (
                    status_code in self.retry_policy.status_codes
                    and retries < self.retry_policy.max_retries
                ):
                    retries += 1
                    await self._sleep_backoff(retries)
                    continue

                self._map_http_error(response, e)

            except Exception as e:
                if isinstance(e, TransportError):
                    raise
                logger.error(
                    f"Unexpected transport failure on request to {url}: {e}",
                    exc_info=True,
                )
                raise TransportError(f"Unexpected transport error: {str(e)}") from e
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                if self.metrics_hook:
                    try:
                        self.metrics_hook(url, duration_ms, success)
                    except Exception as me:
                        logger.error(f"Metrics hook execution failed: {me}")

    async def request_stream(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        content: Optional[Any] = None,
        auth_hook: Optional[Callable[[Dict[str, str]], None]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[bytes]:
        """Execute a streaming HTTP request, yielding raw payload bytes."""
        headers_dict = dict(headers) if headers else {}
        if auth_hook:
            auth_hook(headers_dict)

        timeout = httpx.Timeout(
            connect=self.timeout_policy.connect,
            read=self.timeout_policy.read,
            write=self.timeout_policy.write,
            pool=self.timeout_policy.pool,
        )

        request = self.client.build_request(
            method=method,
            url=url,
            headers=headers_dict,
            json=json,
            params=params,
            content=content,
            timeout=timeout,
            **kwargs,
        )

        for middleware in self.request_middlewares:
            request = await middleware(request)

        try:
            # Construct streaming connection contexts
            async with self.client.stream(
                method=method,
                url=url,
                headers=headers_dict,
                json=json,
                params=params,
                content=content,
                timeout=timeout,
                **kwargs,
            ) as response:
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    self._map_http_error(response, e)

                for resp_middleware in self.response_middlewares:
                    response = await resp_middleware(response)

                async for chunk in response.aiter_bytes():
                    yield chunk

        except httpx.TimeoutException as e:
            raise TransportTimeoutError(f"Streaming request timed out: {str(e)}") from e
        except httpx.NetworkError as e:
            raise TransportNetworkError(f"Streaming network failure: {str(e)}") from e
        except TransportHTTPError:
            raise
        except Exception as e:
            raise TransportError(f"Unexpected streaming error: {str(e)}") from e

    async def _sleep_backoff(self, attempt: int) -> None:
        sleep_time = self.retry_policy.backoff_factor * (2 ** (attempt - 1))
        logger.info(f"Retrying HTTP request. Sleeping for {sleep_time:.2f}s...")
        await asyncio.sleep(sleep_time)

    def _map_http_error(
        self, response: httpx.Response, origin: httpx.HTTPStatusError
    ) -> None:
        status_code = response.status_code
        message = f"HTTP Error {status_code}: {response.text}"
        if status_code == 401:
            raise TransportUnauthorizedError(
                message, status_code=status_code, response_body=response.text
            ) from origin
        elif status_code == 403:
            raise TransportForbiddenError(
                message, status_code=status_code, response_body=response.text
            ) from origin
        elif status_code == 429:
            raise TransportRateLimitError(
                message, status_code=status_code, response_body=response.text
            ) from origin
        else:
            raise TransportHTTPError(
                message, status_code=status_code, response_body=response.text
            ) from origin
