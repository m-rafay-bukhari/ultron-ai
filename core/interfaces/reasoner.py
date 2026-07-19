from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.response import AgentResponse


class BaseReasoner(ABC):
    """Abstract interface for AI reasoning engines."""

    @abstractmethod
    async def reason(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Process a prompt with optional context and return a structured agent response."""
        pass
