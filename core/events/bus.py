import asyncio
import logging
from typing import Dict, List, Type, TypeVar, Any
from core.interfaces.event_bus import BaseEventBus, EventHandler
from models.event import BaseEvent

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseEvent)


class EventBus(BaseEventBus):
    """Concrete implementation of the typed publish/subscribe event system."""

    def __init__(self) -> None:
        self._handlers: Dict[Type[Any], List[EventHandler[Any]]] = {}
        self._wildcard_handlers: List[EventHandler[BaseEvent]] = []
        self._lock = asyncio.Lock()

    async def publish(self, event: BaseEvent) -> None:
        """Publish a typed event to all active subscribers and wildcard subscribers."""
        event_type = type(event)

        # Gather handlers for this specific event type
        handlers_to_run = list(self._handlers.get(event_type, []))
        # Gather wildcard handlers (listening to all events)
        wildcard_to_run = list(self._wildcard_handlers)

        if not handlers_to_run and not wildcard_to_run:
            logger.debug(
                f"No subscribers registered for event type: {event_type.__name__}"
            )
            return

        # Spawn all handlers concurrently in background tasks without blocking the publisher
        for handler in handlers_to_run:
            asyncio.create_task(self._safely_execute(handler, event))
        for handler in wildcard_to_run:
            asyncio.create_task(self._safely_execute(handler, event))

    def subscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Register an async callback handler for a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.info(
                f"Subscribed {handler.__name__ if hasattr(handler, '__name__') else str(handler)} to {event_type.__name__}"
            )

    def unsubscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Unsubscribe a callback handler from a specific event type."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.info(f"Unsubscribed handler from {event_type.__name__}")

    def subscribe_all(self, handler: EventHandler[BaseEvent]) -> None:
        """Subscribe to all events (useful for logging, telemetry, or WebSockets gateways)."""
        if handler not in self._wildcard_handlers:
            self._wildcard_handlers.append(handler)
            logger.info("Subscribed wildcard handler to all events")

    def unsubscribe_all(self, handler: EventHandler[BaseEvent]) -> None:
        """Unsubscribe a wildcard handler."""
        if handler in self._wildcard_handlers:
            self._wildcard_handlers.remove(handler)
            logger.info("Unsubscribed wildcard handler")

    async def _safely_execute(
        self, handler: EventHandler[Any], event: BaseEvent
    ) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Error executing event handler {handler} for event {event.event_type}: {e}",
                exc_info=True,
            )
            # Ensure handlers don't crash the publisher
