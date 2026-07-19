import logging
from typing import Dict, List, Type, Set
from services.ai.provider import BaseModelProvider, ProviderCapability
from services.ai.exceptions import (
    DuplicateProviderError,
    ProviderNotFoundError,
    InvalidModelConfigError,
)

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry to manage and validate concrete LLM provider classes."""

    def __init__(self) -> None:
        self._providers: Dict[str, Type[BaseModelProvider]] = {}

    def register(self, name: str, provider_cls: Type[BaseModelProvider]) -> None:
        """Register a provider class under a name (e.g. 'openai')."""
        name_clean = name.strip().lower()
        if not name_clean:
            raise InvalidModelConfigError("Provider name cannot be empty.")

        # Validation: Verify class inherits from BaseModelProvider
        if not issubclass(provider_cls, BaseModelProvider):
            raise InvalidModelConfigError(
                f"Class '{provider_cls.__name__}' must inherit from BaseModelProvider."
            )

        if name_clean in self._providers:
            raise DuplicateProviderError(f"Provider '{name}' is already registered.")

        self._providers[name_clean] = provider_cls
        logger.info(f"Registered provider: '{name_clean}'")

    def get(self, name: str) -> Type[BaseModelProvider]:
        """Lookup a provider class by name."""
        name_clean = name.strip().lower()
        if name_clean not in self._providers:
            raise ProviderNotFoundError(f"Provider '{name}' is not registered.")
        return self._providers[name_clean]

    def contains(self, name: str) -> bool:
        """Check if a provider name is registered."""
        return name.strip().lower() in self._providers

    def list_all(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    def filter_by_capabilities(self, required: Set[ProviderCapability]) -> List[str]:
        """Filter and return provider names matching all required capabilities."""
        matching = []
        for name, cls in self._providers.items():
            capabilities = getattr(cls, "capabilities", [])
            if required.issubset(set(capabilities)):
                matching.append(name)
        return matching


class ModelRegistry(ProviderRegistry):
    """Backwards-compatible wrapper over ProviderRegistry to maintain existing tests and bindings."""

    def register_provider(
        self, provider_type: str, provider_cls: Type[BaseModelProvider]
    ) -> None:
        """Register a provider class (ModelManager compat wrapper)."""
        self.register(provider_type, provider_cls)

    def get_provider_class(self, provider_type: str) -> Type[BaseModelProvider]:
        """Lookup registered provider class (ModelManager compat wrapper)."""
        return self.get(provider_type)

    def list_providers(self) -> List[str]:
        """List registered provider names (ModelManager compat wrapper)."""
        return self.list_all()
