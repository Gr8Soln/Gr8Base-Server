from collections import defaultdict
from collections.abc import Callable
from typing import Any

from app.application.ports.events.event_bus_port import DomainEvent, EventBusPort
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


class InMemoryEventBus(EventBusPort):
    """Simple in-memory publish/subscribe event bus.

    Thread-safe for async usage. Subscribers are called in order
    of registration. Exceptions in handlers are logged but do not
    prevent other handlers from running.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[DomainEvent], Any]]] = defaultdict(list)

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._subscribers.get(event.event_type, [])
        if not handlers:
            return
        logger.info("event_published", event_type=event.event_type, event_id=str(event.event_id))
        for handler in handlers:
            try:
                result = handler(event)
                # Support both sync and async handlers
                if hasattr(result, "__await__"):
                    await result
            except Exception as e:
                logger.error(
                    "event_handler_failed",
                    event_type=event.event_type,
                    handler=handler.__name__,
                    error=str(e),
                )

    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Any]) -> None:
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.info("event_subscribed", event_type=event_type, handler=handler.__name__)

    def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], Any]) -> None:
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.info("event_unsubscribed", event_type=event_type, handler=handler.__name__)


# Singleton event bus instance
_event_bus: InMemoryEventBus | None = None


def get_event_bus() -> InMemoryEventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
    return _event_bus
