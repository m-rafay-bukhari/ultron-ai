from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    """Configuration settings for a specific user."""

    theme: str = Field(default="dark", description="UI theme preference")
    voice_enabled: bool = Field(
        default=False, description="Whether voice interaction is enabled"
    )
    voice_name: str = Field(default="default", description="Preferred voice model/name")
    local_execution_only: bool = Field(
        default=True, description="Strictly run only local models/tools"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict, description="Additional custom user preferences"
    )


class UserProfile(BaseModel):
    """User profile data for personalization."""

    id: str = Field(..., description="Unique identifier for the user")
    username: str = Field(..., description="Display username")
    email: Optional[str] = Field(None, description="Optional user email")
    settings: UserSettings = Field(
        default_factory=UserSettings, description="User settings configuration"
    )
