import logging
from typing import Dict, Any, Optional
from core.interfaces.reasoner import BaseReasoner
from models.response import AgentResponse

logger = logging.getLogger(__name__)


class Reasoner(BaseReasoner):
    """Reasoning engine implementation.

    Accepts system models and configurations, running LLM inference.
    (AI integrations like Ollama should be plugged in here later).
    """

    def __init__(self, model_name: str = "default-local") -> None:
        self.model_name = model_name

    async def reason(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """Skeletal reasoning implementation."""
        logger.info(f"Reasoner executing with model={self.model_name}")
        # Skeletal response without business logic execution
        return AgentResponse(
            content=f"Skeletal reasoning output for: '{prompt}'",
            tool_calls=[],
            metadata={"model": self.model_name},
        )
