import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_type: str = ""


class EventBusPort(ABC):
    """Abstract port for event publishing and subscription.

    Designed for future migration to distributed event buses
    (Redis Pub/Sub, Kafka, RabbitMQ, AWS SNS/SQS).
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to all registered subscribers."""
        ...

    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], Any]) -> None:
        """Register a handler for a specific event type."""
        ...

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], Any]) -> None:
        """Remove a handler for a specific event type."""
        ...
