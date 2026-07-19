from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStep(BaseModel):
    """A single step in an orchestration workflow."""

    id: str = Field(..., description="Unique step identifier")
    name: str = Field(..., description="Human-readable step name")
    action_type: str = Field(
        ...,
        description="Action/tool/agent type (e.g. tool, reasoning, service)",
    )
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="Execution parameters"
    )
    status: WorkflowStatus = Field(
        default=WorkflowStatus.PENDING, description="Current status of the step"
    )
    depends_on: List[str] = Field(
        default_factory=list, description="IDs of steps this step depends on"
    )
    output: Optional[Any] = Field(
        default=None, description="Result output of the step execution"
    )
    error: Optional[str] = Field(
        default=None, description="Error message if step failed"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Start execution timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="End execution timestamp"
    )


class Workflow(BaseModel):
    """A multi-step orchestration workflow representing a complex user goal."""

    id: str = Field(..., description="Unique workflow identifier")
    goal: str = Field(..., description="The user's original goal description")
    steps: List[WorkflowStep] = Field(
        default_factory=list, description="List of steps in the workflow"
    )
    status: WorkflowStatus = Field(
        default=WorkflowStatus.PENDING, description="Overall status of the workflow"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary workflow metadata"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Workflow run start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Workflow run end timestamp"
    )
