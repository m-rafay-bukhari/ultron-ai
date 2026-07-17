from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from models.memory import MemoryEntry, MemoryType

class BaseMemory(ABC):
    """Abstract interface for storing and retrieving memories (short-term, long-term, semantic, episodic)."""

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
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        """Search relevant memories using vector/semantic search or keyword search."""
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored memories."""
        pass
