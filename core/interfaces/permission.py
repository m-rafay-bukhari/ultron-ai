from abc import ABC, abstractmethod
from typing import Optional
from models.permission import PermissionRule, PermissionScope, PermissionLevel

class BasePermissionManager(ABC):
    """Abstract interface for managing tool execution and command permissions."""

    @abstractmethod
    async def check_permission(self, scope: PermissionScope, target: str) -> PermissionLevel:
        """Check if an action is allowed, denied, or needs user confirmation."""
        pass

    @abstractmethod
    async def request_user_permission(self, scope: PermissionScope, target: str, reason: Optional[str] = None) -> bool:
        """Prompt the user for permission to execute a specific action."""
        pass

    @abstractmethod
    def add_rule(self, rule: PermissionRule) -> None:
        """Add a persistent permission rule."""
        pass

    @abstractmethod
    def remove_rule(self, rule_id: str) -> None:
        """Remove a permission rule by its ID."""
        pass
