from abc import ABC, abstractmethod
from models.tool import ToolExecutionRequest, ToolExecutionResult
from models.workflow import WorkflowStep


class BaseExecutor(ABC):
    """Abstract interface for the action and tool execution layer."""

    @abstractmethod
    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Locate, validate, and execute a tool with permission checks applied."""
        pass

    @abstractmethod
    async def execute_step(self, step: WorkflowStep) -> WorkflowStep:
        """Execute a single workflow step, returning the updated step with output/errors."""
        pass
