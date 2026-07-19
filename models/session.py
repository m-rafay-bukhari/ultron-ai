from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class SessionState(BaseModel):
    """Current dynamic state of an active session."""

    active_agent: Optional[str] = Field(
        default=None, description="Currently active agent ID or name"
    )
    current_workflow_id: Optional[str] = Field(
        default=None, description="Currently running workflow ID"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary temporary session metadata"
    )


class Session(BaseModel):
    """An active user session in ULTRON."""

    id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="ID of the user this session belongs to")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Session creation time",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update time",
    )
    state: SessionState = Field(
        default_factory=lambda: SessionState(), description="Current session state"
    )
