from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from models.memory import MemoryEntry, MemoryType


class BaseMemoryRepository(ABC):
    """Abstract interface for storing and retrieving memories semantic and long-term."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the storage engine."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the storage engine."""
        pass

    @abstractmethod
    async def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        pass

    @abstractmethod
    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory by ID."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 5,
        memory_type: Optional[MemoryType] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryEntry]:
        """Search relevant memories using vector/semantic search."""
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored memories."""
        pass


class BaseConfigRepository(ABC):
    """Abstract interface for key-value configuration storage."""

    @abstractmethod
    async def connect(self) -> None:
        """Establish a connection to the storage engine."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the connection to the storage engine."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by its key."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store a key-value pair with an optional Time-To-Live (TTL)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key-value pair."""
        pass
