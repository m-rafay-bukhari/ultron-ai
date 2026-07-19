import pytest
from typing import Dict, Any, Optional, AsyncIterator
from services.ai import (
    BaseModelProvider,
    ProviderCapability,
    ProviderRegistry,
    ProviderDiscovery,
    DuplicateProviderError,
    ProviderNotFoundError,
    InvalidModelConfigError,
)


class DummyBaseProvider(BaseModelProvider):
    """Skeletal provider class to register during unit tests."""

    async def load(self) -> None:
        pass

    async def unload(self) -> None:
        pass

    async def check_health(self) -> bool:
        return True

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        return ""

    async def generate_stream(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        yield ""


class InvalidClass:
    """Class that does not inherit from BaseModelProvider for validation testing."""

    pass


def test_provider_registration() -> None:
    """Verify standard provider registration."""
    registry = ProviderRegistry()
    registry.register("dummy", DummyBaseProvider)

    assert registry.contains("dummy") is True
    assert registry.get("dummy") is DummyBaseProvider
    assert "dummy" in registry.list_all()


def test_provider_duplicate_registration() -> None:
    """Verify duplicate provider registration throws DuplicateProviderError."""
    registry = ProviderRegistry()
    registry.register("dummy", DummyBaseProvider)

    with pytest.raises(DuplicateProviderError):
        registry.register("dummy", DummyBaseProvider)


def test_provider_lookup_invalid() -> None:
    """Verify looking up unregistered provider throws ProviderNotFoundError."""
    registry = ProviderRegistry()

    with pytest.raises(ProviderNotFoundError):
        registry.get("nonexistent")


def test_provider_invalid_class() -> None:
    """Verify registering a class that does not inherit from BaseModelProvider throws InvalidModelConfigError."""
    registry = ProviderRegistry()

    with pytest.raises(InvalidModelConfigError):
        # Mypy will complain here but we cast to Type[BaseModelProvider] to test runtime validation
        registry.register("invalid", InvalidClass)  # type: ignore


def test_provider_capability_filtering() -> None:
    """Verify capability-based filtering returns correct matches."""
    registry = ProviderRegistry()

    class ChatStreamProvider(DummyBaseProvider):
        capabilities = [ProviderCapability.CHAT, ProviderCapability.STREAMING]

    class EmbeddingsProvider(DummyBaseProvider):
        capabilities = [ProviderCapability.EMBEDDINGS]

    registry.register("chat_stream", ChatStreamProvider)
    registry.register("embeddings_only", EmbeddingsProvider)

    # Filter for chat capabilities
    chat_matches = registry.filter_by_capabilities({ProviderCapability.CHAT})
    assert "chat_stream" in chat_matches
    assert "embeddings_only" not in chat_matches

    # Filter for embeddings capabilities
    embed_matches = registry.filter_by_capabilities({ProviderCapability.EMBEDDINGS})
    assert "embeddings_only" in embed_matches
    assert "chat_stream" not in embed_matches

    # Filter for both chat and streaming capabilities
    both_matches = registry.filter_by_capabilities(
        {ProviderCapability.CHAT, ProviderCapability.STREAMING}
    )
    assert "chat_stream" in both_matches
    assert "embeddings_only" not in both_matches


def test_provider_discovery() -> None:
    """Verify dynamic package discovery walk successfully registers subclasses."""
    registry = ProviderRegistry()
    discovery = ProviderDiscovery(registry=registry)

    # Discover from our test mock_providers package
    discovery.discover_and_register("tests.mock_providers")

    assert registry.contains("first") is True
    assert registry.contains("second") is True

    first_cls = registry.get("first")
    second_cls = registry.get("second")

    assert first_cls.capabilities == [
        ProviderCapability.CHAT,
        ProviderCapability.STREAMING,
    ]
    assert second_cls.capabilities == [
        ProviderCapability.EMBEDDINGS,
        ProviderCapability.VISION,
    ]
