from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any, Type, TypeVar
from models.event import BaseEvent

T = TypeVar("T", bound=BaseEvent)
EventHandler = Callable[[T], Coroutine[Any, Any, None]]

class BaseEventBus(ABC):
    """Abstract interface for a typed publish/subscribe event system."""

    @abstractmethod
    async def publish(self, event: BaseEvent) -> None:
        """Publish a typed event to all active subscribers."""
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Register an async callback handler for a specific event type."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: Type[T], handler: EventHandler[T]) -> None:
        """Unsubscribe a callback handler from a specific event type."""
        pass
