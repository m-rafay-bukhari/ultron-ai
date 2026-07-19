from typing import Dict, Any, Optional
from models.user import UserProfile
from models.session import Session


class ExecutionContext:
    """Represents the context surrounding a specific execution flow or user interaction.

    Includes the session details, active user profile, and arbitrary key-value environmental context.
    """

    def __init__(
        self,
        session: Session,
        user_profile: UserProfile,
        variables: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.session = session
        self.user_profile = user_profile
        self.variables = variables or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def delete(self, key: str) -> None:
        if key in self.variables:
            del self.variables[key]
