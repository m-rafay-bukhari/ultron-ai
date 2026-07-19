from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, Optional, List, AsyncIterator
from services.ai.models import ModelConfig, ModelMetadata


class ModelStatus(str, Enum):
    """Execution status and state transitions for loaded models."""

    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    FAILED = "failed"


class ProviderCapability(str, Enum):
    """Supported capabilities of model providers."""

    CHAT = "chat"
    STREAMING = "streaming"
    EMBEDDINGS = "embeddings"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    REASONING = "reasoning"


class BaseModelProvider(ABC):
    """Abstract base class representing a unified target execution provider for LLMs."""

    # Provider identification and static capabilities metadata
    provider_name: Optional[str] = None
    capabilities: List[ProviderCapability] = []

    def __init__(self, config: ModelConfig, metadata: ModelMetadata) -> None:
        self._config = config
        self._metadata = metadata
        self._status = ModelStatus.UNLOADED

    @property
    def config(self) -> ModelConfig:
        """Get the model configuration settings."""
        return self._config

    @property
    def metadata(self) -> ModelMetadata:
        """Get the static model capabilities and specifications."""
        return self._metadata

    @property
    def status(self) -> ModelStatus:
        """Get the current loaded state of the model provider."""
        return self._status

    @status.setter
    def status(self, value: ModelStatus) -> None:
        """Update the loaded state of the model provider."""
        self._status = value

    @abstractmethod
    async def load(self) -> None:
        """Initialize the provider connection, client libraries, or local files."""
        pass

    @abstractmethod
    async def unload(self) -> None:
        """Release provider memory allocations or socket references."""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check the status of the connection to the provider's endpoint."""
        pass

    @abstractmethod
    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a complete text generation payload."""
        pass

    @abstractmethod
    def generate_stream(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        """Generate a token-streaming completion payload."""
        pass
