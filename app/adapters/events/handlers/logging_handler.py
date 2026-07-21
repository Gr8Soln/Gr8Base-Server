from app.application.ports.events.event_bus_port import DomainEvent
from app.infrastructure.observability.structlog_setup import get_logger

logger = get_logger(__name__)


async def log_event(event: DomainEvent) -> None:
    """Log every domain event with its type and payload summary."""
    logger.info(
        "domain_event",
        event_type=event.event_type,
        event_id=str(event.event_id),
        timestamp=str(event.timestamp),
        **{
            k: v
            for k, v in event.__dict__.items()
            if k not in ("event_id", "timestamp", "event_type")
        },
    )
