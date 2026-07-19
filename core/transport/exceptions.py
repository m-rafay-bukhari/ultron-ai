from core.exceptions import UltronException


class TransportError(UltronException):
    """Base exception for all HTTP transport errors."""

    pass


class TransportTimeoutError(TransportError):
    """Raised when an HTTP request times out."""

    pass


class TransportNetworkError(TransportError):
    """Raised on connection and network socket failures."""

    pass


class TransportHTTPError(TransportError):
    """Raised when an HTTP response contains an error status code (>= 400)."""

    def __init__(self, message: str, status_code: int, response_body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TransportRateLimitError(TransportHTTPError):
    """Raised when an HTTP 429 Too Many Requests status is received."""

    pass


class TransportUnauthorizedError(TransportHTTPError):
    """Raised when an HTTP 401 Unauthorized status is received."""

    pass


class TransportForbiddenError(TransportHTTPError):
    """Raised when an HTTP 403 Forbidden status is received."""

    pass
