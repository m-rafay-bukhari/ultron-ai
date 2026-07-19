from core.exceptions import UltronException


class ModelManagerError(UltronException):
    """Base exception class for all Model Manager errors."""

    pass


class ModelNotFoundError(ModelManagerError):
    """Raised when a requested model ID is not registered or found."""

    pass


class ProviderNotFoundError(ModelManagerError):
    """Raised when a requested provider type is not registered."""

    pass


class ModelLoadError(ModelManagerError):
    """Raised when a model instance fails to load or unload."""

    pass


class ModelExecutionError(ModelManagerError):
    """Raised when a model fails during prompt generation or streaming."""

    pass


class DuplicateModelError(ModelManagerError):
    """Raised when a model ID is registered more than once."""

    pass


class DuplicateProviderError(ModelManagerError):
    """Raised when a provider type is registered more than once."""

    pass


class InvalidModelConfigError(ModelManagerError):
    """Raised when model configuration validation fails."""

    pass
