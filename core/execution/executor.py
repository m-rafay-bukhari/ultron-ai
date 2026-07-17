import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Awaitable
from core.interfaces.executor import BaseExecutor
from core.interfaces.permission import BasePermissionManager
from core.interfaces.event_bus import BaseEventBus
from core.interfaces.tool import BaseTool
from models.tool import ToolExecutionRequest, ToolExecutionResult
from models.workflow import WorkflowStatus, WorkflowStep
from models.event import ToolExecuted
from models.permission import PermissionScope, PermissionLevel
from core.exceptions import ToolNotFoundException, PermissionDeniedException

logger = logging.getLogger(__name__)

class Executor(BaseExecutor):
    """Executes tools and actions in the system, enforcing permission rules and triggering telemetry/events."""

    def __init__(
        self, 
        permission_manager: BasePermissionManager, 
        event_bus: BaseEventBus,
        tool_resolver: Callable[[str], Awaitable[BaseTool]]
    ) -> None:
        self.permission_manager = permission_manager
        self.event_bus = event_bus
        self.tool_resolver = tool_resolver

    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        """Resolve a tool, check permissions, execute, log metrics, and publish events."""
        start_time = time.perf_counter()
        tool_name = request.tool_name
        logger.info(f"Executor received execution request for tool: {tool_name}")

        try:
            # Resolve tool
            tool = await self.tool_resolver(tool_name)
        except Exception as e:
            logger.error(f"Failed to resolve tool {tool_name}: {e}")
            raise ToolNotFoundException(f"Tool {tool_name} not found or could not be loaded")

        # Determine permission scope (e.g. from tool metadata/package name)
        scope = PermissionScope.SYSTEM
        if "filesystem" in tool_name or "file" in tool_name:
            scope = PermissionScope.FILE_SYSTEM
        elif "terminal" in tool_name or "cmd" in tool_name:
            scope = PermissionScope.TERMINAL
        elif "browser" in tool_name:
            scope = PermissionScope.BROWSER

        # Enforce permission rules
        perm_level = await self.permission_manager.check_permission(scope, tool_name)
        if perm_level == PermissionLevel.DENY:
            raise PermissionDeniedException(f"Execution of tool {tool_name} is denied by security policy")
        elif perm_level == PermissionLevel.PROMPT:
            allowed = await self.permission_manager.request_user_permission(
                scope, tool_name, reason="Execution requested by agent"
            )
            if not allowed:
                raise PermissionDeniedException(f"User denied permission to execute tool {tool_name}")

        success = False
        output = None
        error_msg = None

        try:
            # Run the tool
            result = await tool.execute(request.arguments)
            success = result.success
            output = result.output
            error_msg = result.error
        except Exception as e:
            logger.error(f"Error during execution of tool {tool_name}: {e}", exc_info=True)
            success = False
            error_msg = str(e)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Publish execution event
        await self.event_bus.publish(
            ToolExecuted(
                tool_name=tool_name,
                arguments=request.arguments,
                success=success,
                execution_time_ms=duration_ms,
                error=error_msg
            )
        )

        return ToolExecutionResult(
            tool_name=tool_name,
            success=success,
            output=output,
            error=error_msg,
            execution_time_ms=duration_ms
        )

    async def execute_step(self, step: WorkflowStep) -> WorkflowStep:
        """Execute a single workflow step using the executor's tool execution framework."""
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.now(timezone.utc)

        if step.action_type == "tool":
            try:
                request = ToolExecutionRequest(
                    tool_name=step.arguments.get("tool_name", ""),
                    arguments=step.arguments.get("args", {}),
                )
                result = await self.execute_tool(request)
                if result.success:
                    step.status = WorkflowStatus.COMPLETED
                    step.output = result.output
                else:
                    step.status = WorkflowStatus.FAILED
                    step.error = result.error
            except Exception as e:
                step.status = WorkflowStatus.FAILED
                step.error = str(e)
        else:
            # Generic/non-tool steps
            step.status = WorkflowStatus.COMPLETED
            step.output = f"Executed step: {step.name}"

        step.completed_at = datetime.now(timezone.utc)
        return step
