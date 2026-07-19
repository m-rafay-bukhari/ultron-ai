import logging
from typing import Dict, Any, Optional
from uuid import uuid4
from core.interfaces.planner import BasePlanner
from core.interfaces.reasoner import BaseReasoner
from models.workflow import Workflow

logger = logging.getLogger(__name__)


class Planner(BasePlanner):
    """Generates structured execution plans/workflows using an underlying Reasoner."""

    def __init__(self, reasoner: BaseReasoner) -> None:
        self.reasoner = reasoner

    async def create_plan(
        self, goal: str, context: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Create a plan by reasoning about the goal."""
        logger.info(f"Planner creating plan for goal: '{goal}'")
        # In the future, this would construct a prompt from template, call reasoning, and parse output.
        # Stub response matching Workflow structure:
        return Workflow(
            id=str(uuid4()),
            goal=goal,
            steps=[],
            metadata={"planner_model": getattr(self.reasoner, "model_name", "unknown")},
        )
