from abc import ABC, abstractmethod
from models.workflow import WorkflowStatus, WorkflowStep


class BaseWorkflow(ABC):
    """Abstract interface for managing and executing a multi-step workflow."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Get the unique workflow ID."""
        pass

    @property
    @abstractmethod
    def status(self) -> WorkflowStatus:
        """Get the current execution status of the workflow."""
        pass

    @abstractmethod
    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        pass

    @abstractmethod
    async def run(self) -> WorkflowStatus:
        """Run the workflow steps sequentially or concurrently depending on dependencies."""
        pass

    @abstractmethod
    async def cancel(self) -> None:
        """Cancel the workflow execution."""
        pass
