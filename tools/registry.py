import logging
from typing import Dict
from core.interfaces.tool import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Manages the registration and lookup of executable tools."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool instance."""
        name = tool.metadata.name
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def get(self, name: str) -> BaseTool:
        """Retrieve a tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool {name} is not registered")
        return self._tools[name]

    def list_tools(self) -> Dict[str, BaseTool]:
        """Return all registered tools."""
        return dict(self._tools)

    def contains(self, name: str) -> bool:
        """Check if a tool name is registered."""
        return name in self._tools
