from typing import Optional
from core.interfaces.event_bus import BaseEventBus
from core.interfaces.storage import BaseStorage
from core.interfaces.memory import BaseMemory
from core.interfaces.reasoner import BaseReasoner
from core.interfaces.planner import BasePlanner
from core.interfaces.executor import BaseExecutor
from core.interfaces.permission import BasePermissionManager

class Container:
    """Dependency Injection Container for managing service lifecycles and instances.
    
    Avoids global state by allowing instances to be registered and resolved programmatically.
    """

    def __init__(self) -> None:
        self._event_bus: Optional[BaseEventBus] = None
        self._storage: Optional[BaseStorage] = None
        self._memory: Optional[BaseMemory] = None
        self._reasoner: Optional[BaseReasoner] = None
        self._planner: Optional[BasePlanner] = None
        self._executor: Optional[BaseExecutor] = None
        self._permission_manager: Optional[BasePermissionManager] = None

    @property
    def event_bus(self) -> BaseEventBus:
        if not self._event_bus:
            raise RuntimeError("EventBus dependency not registered")
        return self._event_bus

    @event_bus.setter
    def event_bus(self, instance: BaseEventBus) -> None:
        self._event_bus = instance

    @property
    def storage(self) -> BaseStorage:
        if not self._storage:
            raise RuntimeError("Storage dependency not registered")
        return self._storage

    @storage.setter
    def storage(self, instance: BaseStorage) -> None:
        self._storage = instance

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
