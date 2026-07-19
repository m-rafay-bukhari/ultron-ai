from __future__ import annotations
from typing import Optional, TYPE_CHECKING

# Core Interfaces
from core.interfaces.event_bus import BaseEventBus
from core.interfaces.repository import BaseMemoryRepository, BaseConfigRepository
from core.interfaces.memory import BaseMemory
from core.interfaces.reasoner import BaseReasoner
from core.interfaces.planner import BasePlanner
from core.interfaces.executor import BaseExecutor
from core.interfaces.permission import BasePermissionManager

# Guard infrastructure imports to prevent circular dependencies at runtime
if TYPE_CHECKING:
    from services.ai.config import ModelConfigLoader
    from core.transport.http import AsyncHTTPTransport
    from services.ai.registry import ProviderRegistry
    from services.ai.manager import ModelManager


class Container:
    """Dependency Injection Container for managing service lifecycles and instances.

    Avoids global state by allowing instances to be registered and resolved programmatically.
    """

    def __init__(self) -> None:
        self._event_bus: Optional[BaseEventBus] = None
        self._config_repository: Optional[BaseConfigRepository] = None
        self._memory_repository: Optional[BaseMemoryRepository] = None
        self._memory: Optional[BaseMemory] = None
        self._reasoner: Optional[BaseReasoner] = None
        self._planner: Optional[BasePlanner] = None
        self._executor: Optional[BaseExecutor] = None
        self._permission_manager: Optional[BasePermissionManager] = None

        # AI & Transport Infrastructure
        self._config_loader: Optional[ModelConfigLoader] = None
        self._http_transport: Optional[AsyncHTTPTransport] = None
        self._provider_registry: Optional[ProviderRegistry] = None
        self._model_manager: Optional[ModelManager] = None

    @property
    def event_bus(self) -> BaseEventBus:
        if not self._event_bus:
            raise RuntimeError("EventBus dependency not registered")
        return self._event_bus

    @event_bus.setter
    def event_bus(self, instance: BaseEventBus) -> None:
        self._event_bus = instance

    @property
    def config_repository(self) -> BaseConfigRepository:
        if not self._config_repository:
            raise RuntimeError("Config repository dependency not registered")
        return self._config_repository

    @config_repository.setter
    def config_repository(self, instance: BaseConfigRepository) -> None:
        self._config_repository = instance

    @property
    def memory_repository(self) -> BaseMemoryRepository:
        if not self._memory_repository:
            raise RuntimeError("Memory repository dependency not registered")
        return self._memory_repository

    @memory_repository.setter
    def memory_repository(self, instance: BaseMemoryRepository) -> None:
        self._memory_repository = instance

    @property
    def memory(self) -> BaseMemory:
        if not self._memory:
            raise RuntimeError("Memory dependency not registered")
        return self._memory

    @memory.setter
    def memory(self, instance: BaseMemory) -> None:
        self._memory = instance

    @property
    def reasoner(self) -> BaseReasoner:
        if not self._reasoner:
            raise RuntimeError("Reasoner dependency not registered")
        return self._reasoner

    @reasoner.setter
    def reasoner(self, instance: BaseReasoner) -> None:
        self._reasoner = instance

    @property
    def planner(self) -> BasePlanner:
        if not self._planner:
            raise RuntimeError("Planner dependency not registered")
        return self._planner

    @planner.setter
    def planner(self, instance: BasePlanner) -> None:
        self._planner = instance

    @property
    def executor(self) -> BaseExecutor:
        if not self._executor:
            raise RuntimeError("Executor dependency not registered")
        return self._executor

    @executor.setter
    def executor(self, instance: BaseExecutor) -> None:
        self._executor = instance

    @property
    def permission_manager(self) -> BasePermissionManager:
        if not self._permission_manager:
            raise RuntimeError("PermissionManager dependency not registered")
        return self._permission_manager

    @permission_manager.setter
    def permission_manager(self, instance: BasePermissionManager) -> None:
        self._permission_manager = instance

    # Infrastructure Properties
    @property
    def config_loader(self) -> ModelConfigLoader:
        if not self._config_loader:
            raise RuntimeError("ModelConfigLoader dependency not registered")
        return self._config_loader

    @config_loader.setter
    def config_loader(self, instance: ModelConfigLoader) -> None:
        self._config_loader = instance

    @property
    def http_transport(self) -> AsyncHTTPTransport:
        if not self._http_transport:
            raise RuntimeError("AsyncHTTPTransport dependency not registered")
        return self._http_transport

    @http_transport.setter
    def http_transport(self, instance: AsyncHTTPTransport) -> None:
        self._http_transport = instance

    @property
    def provider_registry(self) -> ProviderRegistry:
        if not self._provider_registry:
            raise RuntimeError("ProviderRegistry dependency not registered")
        return self._provider_registry

    @provider_registry.setter
    def provider_registry(self, instance: ProviderRegistry) -> None:
        self._provider_registry = instance

    @property
    def model_manager(self) -> ModelManager:
        if not self._model_manager:
            raise RuntimeError("ModelManager dependency not registered")
        return self._model_manager

    @model_manager.setter
    def model_manager(self, instance: ModelManager) -> None:
        self._model_manager = instance
