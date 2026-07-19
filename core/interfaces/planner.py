from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from models.workflow import Workflow


class BasePlanner(ABC):
    """Abstract interface for planning and dividing high-level goals into executable workflows."""

    @abstractmethod
    async def create_plan(
        self, goal: str, context: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Analyze a goal and output a structured executable Workflow."""
        pass
