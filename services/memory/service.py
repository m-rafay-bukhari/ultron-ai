import logging
from typing import List, Dict, Any, Optional
from core.interfaces.memory import BaseMemory
from core.interfaces.repository import BaseMemoryRepository
from models.memory import MemoryEntry, MemoryType

logger = logging.getLogger(__name__)


class MemoryService(BaseMemory):
    """Orchestrates short-term and long-term memory operations over a database backend."""

    def __init__(self, memory_repository: BaseMemoryRepository) -> None:
        self.memory_repository = memory_repository

    async def store(self, entry: MemoryEntry) -> bool:
        logger.info(f"MemoryService storing entry {entry.id} (type={entry.type.value})")
        return await self.memory_repository.store(entry)

    async def retrieve(self, memory_id: str) -> Optional[MemoryEntry]:
        logger.info(f"MemoryService retrieving entry {memory_id}")
        return await self.memory_repository.retrieve(memory_id)

    async def search(
        self,
        query: str,
        limit: int = 5,
        memory_type: Optional[MemoryType] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[MemoryEntry]:
        logger.info(f"MemoryService searching memories matching: '{query}'")
        return await self.memory_repository.search(
            query, limit, memory_type, filter_metadata
        )

    async def delete(self, memory_id: str) -> bool:
        logger.info(f"MemoryService deleting entry {memory_id}")
        return await self.memory_repository.delete(memory_id)

    async def clear(self) -> None:
        logger.info("MemoryService clearing all memories")
        await self.memory_repository.clear()
