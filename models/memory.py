from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryEntry(BaseModel):
    """A single unit of memory in ULTRON's memory system."""

    id: str = Field(..., description="Unique memory identifier")
    type: MemoryType = Field(..., description="The classification type of the memory")
    content: str = Field(..., description="The memory content or raw text")
    embedding: Optional[List[float]] = Field(
        None, description="Optional vector embedding representation"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata (e.g. source agent, timestamp, tags)",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time the memory was formed",
    )
    last_accessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Time the memory was last accessed",
    )
    importance: float = Field(
        default=0.5, description="Importance score [0.0, 1.0] for decay logic"
    )
