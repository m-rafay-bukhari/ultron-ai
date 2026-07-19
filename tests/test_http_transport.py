import asyncio
from typing import Any, AsyncIterator
import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.transport import (
    RetryPolicy,
    HTTPClientFactory,
    AsyncHTTPTransport,
    TransportTimeoutError,
    TransportHTTPError,
    TransportRateLimitError,
    TransportUnauthorizedError,
    TransportForbiddenError,
)


def test_connection_pool_reuse() -> None:
    """Verify HTTPClientFactory manages a singleton AsyncClient instance."""
    client1 = HTTPClientFactory.get_client()
    client2 = HTTPClientFactory.get_client()

    assert client1 is client2
    assert not client1.is_closed


@pytest.mark.asyncio
async def test_retry_on_status_codes() -> None:
    """Verify AsyncHTTPTransport retries on configured status codes and eventually succeeds."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False

    # Simulate failing twice with 502, succeeding on the third attempt
    request = httpx.Request("GET", "https://example.com/test")
    res_fail = httpx.Response(status_code=502, request=request)
    res_ok = httpx.Response(status_code=200, request=request, json={"data": "ok"})

    mock_client.build_request.return_value = request
    mock_client.send = AsyncMock(side_effect=[res_fail, res_fail, res_ok])

    retry_policy = RetryPolicy(max_retries=2, backoff_factor=0.01)
    transport = AsyncHTTPTransport(client=mock_client, retry_policy=retry_policy)

    response = await transport.request("GET", "https://example.com/test")
    assert response.status_code == 200
    assert response.json() == {"data": "ok"}
    assert mock_client.send.call_count == 3


@pytest.mark.asyncio
async def test_retry_max_attempts_exceeded() -> None:
    """Verify AsyncHTTPTransport raises custom TransportHTTPError when retry attempts are exhausted."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False

    request = httpx.Request("GET", "https://example.com/test")
    res_fail = httpx.Response(status_code=500, request=request)

    mock_client.build_request.return_value = request
    mock_client.send = AsyncMock(return_value=res_fail)

    retry_policy = RetryPolicy(max_retries=2, backoff_factor=0.01)
    transport = AsyncHTTPTransport(client=mock_client, retry_policy=retry_policy)

    with pytest.raises(TransportHTTPError) as exc_info:
        await transport.request("GET", "https://example.com/test")

    assert exc_info.value.status_code == 500
    assert mock_client.send.call_count == 3  # Initial + 2 retries


@pytest.mark.asyncio
async def test_timeout_policy_trigger() -> None:
    """Verify that read/connect timeouts trigger retries and raise TransportTimeoutError."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False

    request = httpx.Request("GET", "https://example.com/test")
    mock_client.build_request.return_value = request
    mock_client.send = AsyncMock(side_effect=httpx.ReadTimeout("Timeout"))

    retry_policy = RetryPolicy(
        max_retries=1, backoff_factor=0.01, retry_on_timeouts=True
    )
    transport = AsyncHTTPTransport(client=mock_client, retry_policy=retry_policy)

    with pytest.raises(TransportTimeoutError):
        await transport.request("GET", "https://example.com/test")

    assert mock_client.send.call_count == 2


@pytest.mark.asyncio
async def test_error_mapping() -> None:
    """Verify HTTP status codes 401, 403, and 429 are mapped to custom exception subclasses."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False
    request = httpx.Request("GET", "https://example.com/test")
    mock_client.build_request.return_value = request

    transport = AsyncHTTPTransport(client=mock_client)

    # 401 Unauthorized
    mock_client.send = AsyncMock(
        return_value=httpx.Response(status_code=401, request=request)
    )
    with pytest.raises(TransportUnauthorizedError):
        await transport.request("GET", "https://example.com/test")

    # 403 Forbidden
    mock_client.send = AsyncMock(
        return_value=httpx.Response(status_code=403, request=request)
    )
    with pytest.raises(TransportForbiddenError):
        await transport.request("GET", "https://example.com/test")

    # 429 Rate Limit
    mock_client.send = AsyncMock(
        return_value=httpx.Response(status_code=429, request=request)
    )
    with pytest.raises(TransportRateLimitError):
        await transport.request("GET", "https://example.com/test")


@pytest.mark.asyncio
async def test_request_and_response_middleware() -> None:
    """Verify request and response middleware execute and modify payloads dynamically."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False
    request = httpx.Request("GET", "https://example.com/test")
    response = httpx.Response(status_code=200, request=request, json={"initial": True})

    mock_client.build_request.return_value = request
    mock_client.send = AsyncMock(return_value=response)

    # Middleware definitions
    async def append_header_middleware(req: httpx.Request) -> httpx.Request:
        req.headers["X-Custom-Req"] = "req-value"
        return req

    async def rewrite_response_middleware(res: httpx.Response) -> httpx.Response:
        # Note: res.json() uses res.content. We construct new Response for test simplicity
        new_res = httpx.Response(
            status_code=res.status_code,
            headers=res.headers,
            request=res.request,
            json={"intercepted": True},
        )
        return new_res

    transport = AsyncHTTPTransport(
        client=mock_client,
        request_middlewares=[append_header_middleware],
        response_middlewares=[rewrite_response_middleware],
    )

    res_out = await transport.request("GET", "https://example.com/test")
    assert res_out.json() == {"intercepted": True}
    assert request.headers.get("X-Custom-Req") == "req-value"


@pytest.mark.asyncio
async def test_header_injection_and_auth_hook() -> None:
    """Verify custom headers and dynamic authentication hooks inject request headers correctly."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False
    request = httpx.Request("GET", "https://example.com/test")
    response = httpx.Response(status_code=200, request=request)

    mock_client.build_request.side_effect = lambda *args, **kwargs: httpx.Request(
        kwargs.get("method", "GET"),
        kwargs.get("url", ""),
        headers=kwargs.get("headers"),
    )
    mock_client.send = AsyncMock(return_value=response)

    transport = AsyncHTTPTransport(client=mock_client)

    def auth_callback(headers: dict[str, str]) -> None:
        headers["Authorization"] = "Bearer token123"

    _ = await transport.request(
        "GET",
        "https://example.com/test",
        headers={"X-Test-Id": "123"},
        auth_hook=auth_callback,
    )

    req_sent = mock_client.send.call_args[0][0]
    assert req_sent.headers.get("X-Test-Id") == "123"
    assert req_sent.headers.get("Authorization") == "Bearer token123"


@pytest.mark.asyncio
async def test_request_cancellation() -> None:
    """Verify request execution cancels cleanly when task context is cancelled."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False
    request = httpx.Request("GET", "https://example.com/slow")

    mock_client.build_request.return_value = request

    # AsyncMock that simulates infinite wait
    async def slow_send(*args: Any, **kwargs: Any) -> httpx.Response:
        await asyncio.sleep(100)
        return httpx.Response(200)

    mock_client.send = slow_send
    transport = AsyncHTTPTransport(client=mock_client)

    task = asyncio.create_task(transport.request("GET", "https://example.com/slow"))
    await asyncio.sleep(0.02)  # Let it start
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_streaming_response() -> None:
    """Verify streaming response yields byte chunks and maps errors correctly."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.is_closed = False
    request = httpx.Request("GET", "https://example.com/stream")
    response = httpx.Response(status_code=200, request=request)

    # Set up mock response stream generator
    async def mock_aiter_bytes(*args: Any, **kwargs: Any) -> AsyncIterator[bytes]:
        yield b"chunk1"
        yield b"chunk2"

    response.aiter_bytes = mock_aiter_bytes  # type: ignore

    # Mock the stream context manager
    class MockStreamContext:
        async def __aenter__(self) -> httpx.Response:
            return response

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

    mock_client.stream.return_value = MockStreamContext()
    transport = AsyncHTTPTransport(client=mock_client)

    chunks = []
    async for chunk in transport.request_stream("GET", "https://example.com/stream"):
        chunks.append(chunk)

    assert chunks == [b"chunk1", b"chunk2"]
    mock_client.stream.assert_called_once()
