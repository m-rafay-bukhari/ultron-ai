from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    PROMPT = "prompt"


class PermissionScope(str, Enum):
    FILE_SYSTEM = "filesystem"
    TERMINAL = "terminal"
    NETWORK = "network"
    SYSTEM = "system"
    BROWSER = "browser"
    INTEGRATION = "integration"


class PermissionRule(BaseModel):
    """Represents a rule governing execution of tools or system actions."""

    id: str = Field(..., description="Unique rule ID")
    scope: PermissionScope = Field(..., description="The scope of the permission")
    target: str = Field(
        ...,
        description="The target entity (e.g. command prefix, directory path, API endpoint)",
    )
    level: PermissionLevel = Field(
        default=PermissionLevel.PROMPT, description="Action level when rule is matched"
    )
    reason: Optional[str] = Field(None, description="Optional explanation for the rule")
