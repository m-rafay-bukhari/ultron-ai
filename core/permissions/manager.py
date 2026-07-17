import logging
from typing import Dict, Optional
from core.interfaces.permission import BasePermissionManager
from models.permission import PermissionRule, PermissionScope, PermissionLevel

logger = logging.getLogger(__name__)

class PermissionManager(BasePermissionManager):
    """Manages system permission rules, checking target scopes against defined rules."""

    def __init__(self) -> None:
        # Maps rule_id -> PermissionRule
        self._rules: Dict[str, PermissionRule] = {}

    async def check_permission(self, scope: PermissionScope, target: str) -> PermissionLevel:
        """Evaluate rules in order. Defaults to PROMPT if no matching rule is found."""
        # Exact or prefix match evaluation
        for rule in self._rules.values():
            if rule.scope == scope and target.startswith(rule.target):
                logger.info(f"Permission rule match found for {scope}:{target} -> {rule.level.value}")
                return rule.level
        
        # Default behavior: request confirmation for safety
        return PermissionLevel.PROMPT

    async def request_user_permission(self, scope: PermissionScope, target: str, reason: Optional[str] = None) -> bool:
        """Prompt the user for permission. Stub implementation for now."""
        logger.warning(f"Requesting user permission for scope={scope.value}, target={target}, reason={reason}")
        # In a real system, this would block on a WebSocket or UI callback.
        # Since we do not implement business logic, we return False by default.
        return False

    def add_rule(self, rule: PermissionRule) -> None:
        """Add a persistent permission rule."""
        self._rules[rule.id] = rule
        logger.info(f"Added permission rule: {rule.id} (scope={rule.scope.value}, level={rule.level.value})")

    def remove_rule(self, rule_id: str) -> None:
        """Remove a permission rule by its ID."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.info(f"Removed permission rule: {rule_id}")
