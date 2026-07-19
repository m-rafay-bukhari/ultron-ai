from core.exceptions import UltronException


class ToolException(UltronException):
    """Base exception for all tool execution and loading errors."""

    pass


class ToolValidationError(ToolException):
    """Raised when tool arguments fail validation."""

    pass


class ToolExecutionError(ToolException):
    """Raised when tool execution encounters an error."""

    pass


class ToolPermissionDenied(ToolException):
    """Raised when permission to execute a tool is denied."""

    pass
