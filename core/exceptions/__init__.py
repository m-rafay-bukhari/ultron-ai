class UltronException(Exception):
    """Base exception class for all ULTRON AI errors."""

    pass


class WorkflowException(UltronException):
    """Raised when a workflow or step execution fails."""

    pass


class ExecutionException(UltronException):
    """Raised when a command or tool executor fails."""

    pass


class PermissionDeniedException(UltronException):
    """Raised when an operation is blocked by security permissions."""

    pass


class ToolNotFoundException(UltronException):
    """Raised when a requested tool is not registered."""

    pass


class StorageException(UltronException):
    """Raised when storage operations fail."""

    pass


class MemoryException(UltronException):
    """Raised when memory storage/retrieval operations fail."""

    pass


class ConfigurationException(UltronException):
    """Raised when configuration values are invalid or missing."""

    pass
