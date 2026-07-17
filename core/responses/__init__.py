from typing import Any, Dict
from models.response import AgentResponse

def format_agent_response(content: str, tool_calls: list = None, metadata: Dict[str, Any] = None) -> AgentResponse:
    """Utility helper to build an AgentResponse object."""
    return AgentResponse(
        content=content,
        tool_calls=tool_calls or [],
        metadata=metadata or {}
    )
