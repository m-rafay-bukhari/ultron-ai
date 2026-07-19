import pytest
from unittest.mock import AsyncMock, patch
from core.context.container import Container
from core.transport.http import HTTPClientFactory
from backend.app.main import setup_dependencies, on_shutdown, container as app_container
from storage.sqlite.connection import SQLiteConfigRepository
from storage.vector.chromadb import ChromaMemoryRepository


def test_container_unregistered_errors() -> None:
    """Verify that accessing unregistered container properties raises RuntimeError."""
    container = Container()

    with pytest.raises(RuntimeError, match="EventBus dependency not registered"):
        _ = container.event_bus

    with pytest.raises(
        RuntimeError, match="ModelConfigLoader dependency not registered"
    ):
        _ = container.config_loader

    with pytest.raises(
        RuntimeError, match="AsyncHTTPTransport dependency not registered"
    ):
        _ = container.http_transport

    with pytest.raises(
        RuntimeError, match="ProviderRegistry dependency not registered"
    ):
        _ = container.provider_registry

    with pytest.raises(RuntimeError, match="ModelManager dependency not registered"):
        _ = container.model_manager


def test_container_registration_and_singletons() -> None:
    """Verify standard property assignment, dependency retrieval, and singleton behavior."""
    container = Container()

    # Mock instances
    mock_event_bus = AsyncMock()
    mock_loader = AsyncMock()
    mock_transport = AsyncMock()
    mock_registry = AsyncMock()
    mock_manager = AsyncMock()

    # Register
    container.event_bus = mock_event_bus
    container.config_loader = mock_loader
    container.http_transport = mock_transport
    container.provider_registry = mock_registry
    container.model_manager = mock_manager

    # Verify retrieval returns exact singletons
    assert container.event_bus is mock_event_bus
    assert container.config_loader is mock_loader
    assert container.http_transport is mock_transport
    assert container.provider_registry is mock_registry
    assert container.model_manager is mock_manager

    # Verify reassignment resolves correctly
    mock_event_bus_2 = AsyncMock()
    container.event_bus = mock_event_bus_2
    assert container.event_bus is mock_event_bus_2


@pytest.mark.asyncio
async def test_application_lifecycle_startup_and_shutdown() -> None:
    """Verify that startup and shutdown lifecycle hooks initialize, register, and close resources gracefully."""
    # Mock repositories connect/disconnect calls to avoid mutating local DB files
    with (
        patch.object(
            SQLiteConfigRepository, "connect", new_callable=AsyncMock
        ) as mock_sqlite_conn,
        patch.object(
            ChromaMemoryRepository, "connect", new_callable=AsyncMock
        ) as mock_chroma_conn,
        patch.object(
            SQLiteConfigRepository, "disconnect", new_callable=AsyncMock
        ) as mock_sqlite_disc,
        patch.object(
            ChromaMemoryRepository, "disconnect", new_callable=AsyncMock
        ) as mock_chroma_disc,
    ):
        # 1. Run Startup Lifespan hook
        await setup_dependencies()

        # Verify DB connection calls occurred
        mock_sqlite_conn.assert_called_once()
        mock_chroma_conn.assert_called_once()

        # Verify all DI container bindings are correctly established
        assert app_container.event_bus is not None
        assert app_container.config_loader is not None
        assert app_container.http_transport is not None
        assert app_container.provider_registry is not None
        assert app_container.model_manager is not None

        # Verify config is loaded and singleton HTTP pool client exists
        config = app_container.config_loader.get_config()
        assert config.default_model == "ollama-llama3"

        client = HTTPClientFactory.get_client()
        assert not client.is_closed

        # 2. Run Shutdown Lifespan hook
        await on_shutdown()

        # Verify DB disconnect calls occurred
        mock_sqlite_disc.assert_called_once()
        mock_chroma_disc.assert_called_once()

        # Verify HTTP client pool is closed and cleaned up
        assert HTTPClientFactory._client is None
