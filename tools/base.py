import logging
from abc import abstractmethod
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, ValidationError
from core.interfaces.tool import BaseTool
from models.tool import ToolMetadata, ToolExecutionResult

logger = logging.getLogger(__name__)


class BaseToolImpl(BaseTool):
    """Production-grade base class for all ULTRON tools.

    Subclasses must define name, description, and optionally args_model.
    """

    name: str
    description: str
    args_model: Optional[Type[BaseModel]] = None
    requires_permission: bool = False

    @property
    def metadata(self) -> ToolMetadata:
        """Standardized interface metadata generation."""
        schema = self.args_model.model_json_schema() if self.args_model else {}
        return ToolMetadata(
            name=self.name,
            description=self.description,
            args_schema=schema,
            requires_permission=self.requires_permission,
        )

    async def execute(self, arguments: Dict[str, Any]) -> ToolExecutionResult:
        """Standardized interface execution wrapper with input argument validation."""
        import time

        start_time = time.perf_counter()

        # Validate arguments using Pydantic if args_model is provided
        if self.args_model:
            try:
                validated_args = self.args_model(**arguments).model_dump()
            except ValidationError as e:
                logger.error(f"Validation error running tool {self.name}: {e}")
                return ToolExecutionResult(
                    tool_name=self.name,
                    success=False,
                    error=f"Argument validation failed: {str(e)}",
                    execution_time_ms=(time.perf_counter() - start_time) * 1000.0,
                )
        else:
            validated_args = arguments

        try:
            # Execute actual tool logic implemented in subclass
            output = await self._run(validated_args)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolExecutionResult(
                tool_name=self.name,
                success=True,
                output=output,
                execution_time_ms=duration_ms,
            )
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}", exc_info=True)
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return ToolExecutionResult(
                tool_name=self.name,
                success=False,
                error=str(e),
                execution_time_ms=duration_ms,
            )

    @abstractmethod
    async def _run(self, arguments: Dict[str, Any]) -> Any:
        """Subclasses override this to implement execution logic."""
        pass
