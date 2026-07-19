import time
import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """Tracks latency, resource utilization, and performance stats of operations."""

    @staticmethod
    async def track_latency(
        operation_name: str, coro: Callable[[], Awaitable[Any]]
    ) -> Any:
        """Measure latency of an async coroutine call."""
        start = time.perf_counter()
        try:
            return await coro()
        finally:
            duration_ms = (time.perf_counter() - start) * 1000.0
            logger.info(
                f"[PERFORMANCE] Latency for '{operation_name}': {duration_ms:.2f} ms"
            )
