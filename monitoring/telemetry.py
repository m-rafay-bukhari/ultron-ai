import logging
from core.interfaces.event_bus import BaseEventBus
from models.event import BaseEvent

logger = logging.getLogger(__name__)

class TelemetrySystem:
    """Subscribes to EventBus events to track operations, latencies, and system events."""

    def __init__(self, event_bus: BaseEventBus) -> None:
        self.event_bus = event_bus
        # Register a wildcard handler to pipe all events to telemetry logs
        self.event_bus.subscribe_all(self._track_event)

    async def _track_event(self, event: BaseEvent) -> None:
        """Handle and log any event occurring in the system."""
        logger.info(f"[TELEMETRY] Event Occurred: ID={event.event_id} | Type={event.event_type} | Time={event.timestamp}")
        # In a real environment, this might push metrics to Prometheus/OpenTelemetry/etc.
