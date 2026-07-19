import logging
from datetime import datetime, timezone
from typing import List
from core.interfaces.workflow import BaseWorkflow
from core.interfaces.event_bus import BaseEventBus
from core.interfaces.executor import BaseExecutor
from models.workflow import WorkflowStatus, WorkflowStep, Workflow as WorkflowModel
from models.event import WorkflowStarted, WorkflowCompleted

logger = logging.getLogger(__name__)


class WorkflowImpl(BaseWorkflow):
    """Concrete implementation of a multi-step workflow execution coordinator."""

    def __init__(
        self,
        workflow_model: WorkflowModel,
        event_bus: BaseEventBus,
        executor: BaseExecutor,
    ) -> None:
        self._model = workflow_model
        self._event_bus = event_bus
        self._executor = executor
        self._steps: List[WorkflowStep] = []

    @property
    def id(self) -> str:
        return self._model.id

    @property
    def status(self) -> WorkflowStatus:
        return self._model.status

    def add_step(self, step: WorkflowStep) -> None:
        self._steps.append(step)

    async def run(self) -> WorkflowStatus:
        """Run the workflow steps sequentially using the executor."""
        logger.info(f"Running workflow {self.id} for goal: {self._model.goal}")

        self._model.status = WorkflowStatus.RUNNING
        self._model.started_at = datetime.now(timezone.utc)

        await self._event_bus.publish(
            WorkflowStarted(workflow_id=self.id, goal=self._model.goal)
        )

        try:
            # Sequentially run steps using the injected executor
            for step in self._steps:
                if self._model.status == WorkflowStatus.CANCELLED:
                    break

                # Execute step via Executor (the single execution pathway)
                step_result = await self._executor.execute_step(step)
                if step_result.status == WorkflowStatus.FAILED:
                    self._model.status = WorkflowStatus.FAILED
                    self._model.metadata["error"] = step_result.error
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
                    error=self._model.metadata.get("error"),
                )
            )

        return self._model.status

    async def cancel(self) -> None:
        logger.info(f"Cancelling workflow {self.id}")
        self._model.status = WorkflowStatus.CANCELLED
