import logging
from typing import Callable, Any, Coroutine, Dict, Tuple

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manages system cron schedules and background intervals for task planning."""

    def __init__(self) -> None:
        self._schedules: Dict[
            str, Tuple[str, Callable[[], Coroutine[Any, Any, None]]]
        ] = {}

    def schedule_cron(
        self,
        name: str,
        cron_expression: str,
        task: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        logger.info(
            f"Scheduling task '{name}' with cron expression '{cron_expression}'"
        )
        self._schedules[name] = (cron_expression, task)

    def cancel_schedule(self, name: str) -> None:
        logger.info(f"Cancelling scheduled task '{name}'")
        if name in self._schedules:
            del self._schedules[name]
