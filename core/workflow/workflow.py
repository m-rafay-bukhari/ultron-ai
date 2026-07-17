import logging
from datetime import datetime, timezone
from typing import List, Optional
from core.interfaces.workflow import BaseWorkflow, BaseWorkflowStep
from core.interfaces.event_bus import BaseEventBus
from models.workflow import WorkflowStatus, WorkflowStep, Workflow as WorkflowModel
from models.event import WorkflowStarted, WorkflowCompleted

logger = logging.getLogger(__name__)

class WorkflowStepImpl(BaseWorkflowStep):
    """Concrete implementation of a workflow step execution logic."""

    def __init__(self, step_model: WorkflowStep) -> None:
        self._model = step_model

    @property
    def id(self) -> str:
        return self._model.id

    @property
    def name(self) -> str:
        return self._model.name

    async def execute(self) -> Optional[WorkflowStep]:
        """Execute the individual step (to be wired into executor later)."""
        logger.info(f"Executing workflow step {self.id}: {self.name}")
        self._model.status = WorkflowStatus.RUNNING
        self._model.started_at = datetime.now(timezone.utc)
        # Stub execution:
        self._model.status = WorkflowStatus.COMPLETED
        self._model.completed_at = datetime.now(timezone.utc)
        self._model.output = f"Step '{self.name}' completed successfully"
        return self._model


class WorkflowImpl(BaseWorkflow):
    """Concrete implementation of a multi-step workflow execution coordinator."""

    def __init__(self, workflow_model: WorkflowModel, event_bus: BaseEventBus) -> None:
        self._model = workflow_model
        self._event_bus = event_bus
        self._steps: List[BaseWorkflowStep] = []

    @property
    def id(self) -> str:
        return self._model.id

    @property
    def status(self) -> WorkflowStatus:
        return self._model.status

    def add_step(self, step: BaseWorkflowStep) -> None:
        self._steps.append(step)

    async def run(self) -> WorkflowStatus:
        """Run the workflow steps and publish start/completion events."""
        logger.info(f"Running workflow {self.id} for goal: {self._model.goal}")
        
        self._model.status = WorkflowStatus.RUNNING
        self._model.started_at = datetime.now(timezone.utc)
        
        await self._event_bus.publish(
            WorkflowStarted(workflow_id=self.id, goal=self._model.goal)
        )

        try:
            # Sequentially run steps
            for step in self._steps:
                if self._model.status == WorkflowStatus.CANCELLED:
                    break
                
                step_result = await step.execute()
                if step_result and step_result.status == WorkflowStatus.FAILED:
                    self._model.status = WorkflowStatus.FAILED
                    break
            else:
                if self._model.status != WorkflowStatus.CANCELLED:
                    self._model.status = WorkflowStatus.COMPLETED
                    
        except Exception as e:
            logger.error(f"Error executing workflow {self.id}: {e}", exc_info=True)
            self._model.status = WorkflowStatus.FAILED
            self._model.metadata["error"] = str(e)
        finally:
            self._model.completed_at = datetime.now(timezone.utc)
            await self._event_bus.publish(
                WorkflowCompleted(
                    workflow_id=self.id, 
                    status=self._model.status.value,
                    error=self._model.metadata.get("error")
                )
            )
            
        return self._model.status

    async def cancel(self) -> None:
        logger.info(f"Cancelling workflow {self.id}")
        self._model.status = WorkflowStatus.CANCELLED
