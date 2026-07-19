from abc import ABC, abstractmethod
from typing import Dict, Any
from models.tool import ToolMetadata, ToolExecutionResult


class BaseTool(ABC):
    """Abstract interface for all executable tools in the ULTRON OS."""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Return the tool metadata containing name, description, schema, etc."""
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolExecutionResult:
        """Execute the tool with the given arguments."""
        pass
