import logging
from typing import List, Dict, Any, Optional
from core.interfaces.memory import BaseMemory
from core.interfaces.storage import BaseStorage
from models.memory import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)

class MemoryService(BaseMemory):
    """Orchestrates short-term and long-term memory operations over a database backend."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    async def store(self, entry: MemoryEntry) -> bool:
        logger.info(f"MemoryService storing entry {entry.id} (type={entry.type.value})")
        # Store in underlying DB using injected storage
        await self.storage.set(f"mem:{entry.id}", entry.model_dump())
        return True

    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        logger.info(f"MemoryService retrieving entry {memory_id}")
        data = await self.storage.get(f"mem:{memory_id}")
        if data:
            return MemoryEntry(**data)
        return None

    async def search(
        self, 
        query: str, 
        limit: int = 5, 
        memory_type: Optional[MemoryType] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[MemoryEntry]:
        logger.info(f"MemoryService searching memories matching: '{query}'")
        # In a real implementation, this would perform vector lookup via ChromaDB
        return []

    async def delete(self, memory_id: str) -> bool:
        logger.info(f"MemoryService deleting entry {memory_id}")
        return await self.storage.delete(f"mem:{memory_id}")

    async def clear(self) -> None:
        logger.info("MemoryService clearing all memories")
        # In a real implementation, this would truncate tables/indexes
