import logging
from typing import Dict, Any
from core.interfaces.executor import BaseExecutor
from models.tool import ToolExecutionRequest, ToolExecutionResult
from tools.registry import ToolRegistry
from core.exceptions import ToolNotFoundException

logger = logging.getLogger(__name__)

class ToolExecutor:
    """Helper executor scoped specifically for running tools from the local registry."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    async def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Directly invoke a tool from the registry."""
        tool_name = request.tool_name
        if not self.registry.contains(tool_name):
            logger.error(f"Execution failed: Tool '{tool_name}' not found")
            raise ToolNotFoundException(f"Tool '{tool_name}' not registered")

        tool = self.registry.get(tool_name)
        return await tool.execute(request.arguments)
