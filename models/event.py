from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

class BaseEvent(BaseModel):
    """Base class for all system events."""
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique ID for this event occurrence")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Time the event occurred")
    event_type: str = Field(..., description="The name of the event type")

class WorkflowStarted(BaseEvent):
    event_type: str = "WorkflowStarted"
    workflow_id: str
    goal: str

class WorkflowCompleted(BaseEvent):
    event_type: str = "WorkflowCompleted"
    workflow_id: str
    status: str
    error: Optional[str] = None

class ToolExecuted(BaseEvent):
    event_type: str = "ToolExecuted"
    tool_name: str
    arguments: Dict[str, Any]
    success: bool
    execution_time_ms: float
    error: Optional[str] = None

class MemoryStored(BaseEvent):
    event_type: str = "MemoryStored"
    memory_id: str
    memory_type: str
    summary_snippet: str

class ModelLoaded(BaseEvent):
    event_type: str = "ModelLoaded"
    model_name: str
    latency_ms: float

class VoiceStarted(BaseEvent):
    event_type: str = "VoiceStarted"
    source: str = Field(default="user", description="Who started speaking (user or assistant)")

class VoiceFinished(BaseEvent):
    event_type: str = "VoiceFinished"
    source: str
    transcript: Optional[str] = None
