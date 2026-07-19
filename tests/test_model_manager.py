import pytest
from typing import Optional, Dict, Any, AsyncIterator
from services.ai import (
    BaseModelProvider,
    ModelStatus,
    ModelConfig,
    ModelMetadata,
    ModelRegistry,
    ModelManager,
    ModelNotFoundError,
    ProviderNotFoundError,
    ModelLoadError,
    DuplicateModelError,
    DuplicateProviderError,
    InvalidModelConfigError,
)


class MockModelProvider(BaseModelProvider):
    """Mock implementation of BaseModelProvider for testing lifecycle and responses."""

    def __init__(self, config: ModelConfig, metadata: ModelMetadata) -> None:
        super().__init__(config, metadata)
        self.load_called = False
        self.unload_called = False
        self.health_healthy = True

    async def load(self) -> None:
        self.load_called = True

    async def unload(self) -> None:
        self.unload_called = True

    async def check_health(self) -> bool:
        return self.health_healthy

    async def generate(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> str:
        return f"Mock response for: {prompt}"

    async def generate_stream(
        self, prompt: str, options: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[str]:
        yield "Mock "
        yield "stream "
        yield f"for: {prompt}"


class FailingLoadProvider(MockModelProvider):
    """Mock provider that fails during loading to test transition states."""

    async def load(self) -> None:
        raise RuntimeError("Network failure loading weights")


@pytest.fixture
def registry() -> ModelRegistry:
    """Fixture supplying a clean ModelRegistry."""
    return ModelRegistry()


@pytest.fixture
def manager(registry: ModelRegistry) -> ModelManager:
    """Fixture supplying a ModelManager wired with a clean registry."""
    return ModelManager(registry=registry)


def test_provider_registration(registry: ModelRegistry) -> None:
    """Verify standard provider registration and listing."""
    registry.register_provider("mock", MockModelProvider)
    assert "mock" in registry.list_providers()
    assert registry.get_provider_class("mock") is MockModelProvider


def test_duplicate_provider_registration(registry: ModelRegistry) -> None:
    """Verify duplicate provider registration throws custom DuplicateProviderError."""
    registry.register_provider("mock", MockModelProvider)
    with pytest.raises(DuplicateProviderError):
        registry.register_provider("mock", MockModelProvider)


def test_provider_lookup_invalid(registry: ModelRegistry) -> None:
    """Verify querying an unregistered provider throws ProviderNotFoundError."""
    with pytest.raises(ProviderNotFoundError):
        registry.get_provider_class("nonexistent")


def test_model_registration(manager: ModelManager, registry: ModelRegistry) -> None:
    """Verify standard model configuration registration."""
    registry.register_provider("mock", MockModelProvider)
    config = ModelConfig(provider="mock", model_name="llama3")
    metadata = ModelMetadata()

    manager.register_model("model-1", config, metadata)
    assert "model-1" in manager.list_registered_models()
    assert manager.get_model_status("model-1") == ModelStatus.UNLOADED


def test_duplicate_model_registration(
    manager: ModelManager, registry: ModelRegistry
) -> None:
    """Verify duplicate model registration raises DuplicateModelError."""
    registry.register_provider("mock", MockModelProvider)
    config = ModelConfig(provider="mock", model_name="llama3")
    metadata = ModelMetadata()

    manager.register_model("model-1", config, metadata)
    with pytest.raises(DuplicateModelError):
        manager.register_model("model-1", config, metadata)


@pytest.mark.parametrize(
    "model_id,provider,model_name",
    [
        ("", "mock", "llama3"),
        ("model-1", "", "llama3"),
        ("model-1", "mock", ""),
    ],
)
def test_invalid_model_configurations(
    manager: ModelManager,
    registry: ModelRegistry,
    model_id: str,
    provider: str,
    model_name: str,
) -> None:
    """Verify invalid model configurations raise InvalidModelConfigError."""
    registry.register_provider("mock", MockModelProvider)
    config = ModelConfig(provider=provider, model_name=model_name)
    metadata = ModelMetadata()

    with pytest.raises(InvalidModelConfigError):
        manager.register_model(model_id, config, metadata)


@pytest.mark.asyncio
async def test_model_lifecycle(manager: ModelManager, registry: ModelRegistry) -> None:
    """Verify standard model lifecycle: register, load, ready, execution, unload."""
    registry.register_provider("mock", MockModelProvider)
    config = ModelConfig(provider="mock", model_name="llama3")
    metadata = ModelMetadata()

    manager.register_model("model-1", config, metadata)

    # Verify not yet active
    assert len(manager.list_active_models()) == 0
    assert manager.get_model_status("model-1") == ModelStatus.UNLOADED

    # Load model
    await manager.load_model("model-1")
    assert "model-1" in manager.list_active_models()
    assert manager.get_model_status("model-1") == ModelStatus.READY

    model_inst = await manager.get_model("model-1")
    assert isinstance(model_inst, MockModelProvider)
    assert model_inst.load_called is True

    # Generation execution
    res = await manager.generate("model-1", "Hello")
    assert res == "Mock response for: Hello"

    # Streaming execution
    stream_res = []
    async for chunk in manager.generate_stream("model-1", "Hello"):
        stream_res.append(chunk)
    assert "".join(stream_res) == "Mock stream for: Hello"

    # Unload model
    await manager.unload_model("model-1")
    assert len(manager.list_active_models()) == 0
    assert manager.get_model_status("model-1") == ModelStatus.UNLOADED
    assert model_inst.unload_called is True


@pytest.mark.asyncio
async def test_model_lifecycle_failure(
    manager: ModelManager, registry: ModelRegistry
) -> None:
    """Verify model lifecycle failure transitions to FAILED state."""
    registry.register_provider("fail-load", FailingLoadProvider)
    config = ModelConfig(provider="fail-load", model_name="llama3")
    metadata = ModelMetadata()

    manager.register_model("model-fail", config, metadata)

    with pytest.raises(ModelLoadError):
        await manager.load_model("model-fail")

    assert manager.get_model_status("model-fail") == ModelStatus.FAILED


@pytest.mark.asyncio
async def test_model_health_diagnostics(
    manager: ModelManager, registry: ModelRegistry
) -> None:
    """Verify model health monitoring query routes correctly."""
    registry.register_provider("mock", MockModelProvider)
    config = ModelConfig(provider="mock", model_name="llama3")
    metadata = ModelMetadata()

    manager.register_model("model-1", config, metadata)

    # Healthy check
    assert await manager.check_model_health("model-1") is True

    # Unhealthy check
    model_inst = await manager.get_model("model-1")
    assert isinstance(model_inst, MockModelProvider)
    model_inst.health_healthy = False
    assert await manager.check_model_health("model-1") is False


@pytest.mark.asyncio
async def test_model_lookup_errors(manager: ModelManager) -> None:
    """Verify loading, unloading or querying unregistered models throws ModelNotFoundError."""
    with pytest.raises(ModelNotFoundError):
        await manager.load_model("unregistered")

    with pytest.raises(ModelNotFoundError):
        await manager.get_model("unregistered")

    with pytest.raises(ModelNotFoundError):
        await manager.check_model_health("unregistered")
