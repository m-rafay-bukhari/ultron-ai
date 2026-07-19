from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata describing a tool's identity and contract."""

    name: str = Field(..., description="Unique tool name")
    description: str = Field(..., description="Description of what the tool does")
    args_schema: Dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for the tool arguments"
    )
    requires_permission: bool = Field(
        default=False, description="Does the tool require user authorization to run?"
    )


class ToolExecutionRequest(BaseModel):
    """A tool execution payload."""

    tool_name: str = Field(..., description="Target tool name")
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Arguments to execute the tool with"
    )
    context_id: Optional[str] = Field(
        default=None, description="Optional associated execution context/session ID"
    )


class ToolExecutionResult(BaseModel):
    """Result returned from running a tool."""

    tool_name: str = Field(..., description="Tool name that was run")
    success: bool = Field(
        ..., description="Did the execution succeed without unhandled exceptions?"
    )
    output: Any = Field(
        default=None,
        description="The return payload/output of the tool (string, JSON, etc.)",
    )
    error: Optional[str] = Field(
        default=None, description="Error message if success is False"
    )
    execution_time_ms: float = Field(
        default=0.0, description="Time taken to execute the tool"
    )
