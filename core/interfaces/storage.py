from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseStorage(ABC):
    """Abstract interface for storage backend operations (e.g. SQLite, ChromaDB, vector indexes)."""

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

    @abstractmethod
    async def query(self, statement: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Run a custom query against the database engine."""
        pass
