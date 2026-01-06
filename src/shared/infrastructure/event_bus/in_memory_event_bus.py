"""
Shared Infrastructure - In-Memory Event Bus Implementation.
"""

from typing import Callable, Dict, List, Type

from src.shared.infrastructure.logging_config import get_logger
from src.shared.domain.events import DomainEvent, IDomainEventPublisher

logger = get_logger(__name__)


class InMemoryEventBus(IDomainEventPublisher):
    """
    In-memory implementation of the Domain Event Bus.
    """

    def __init__(self):
        """Initialize the event bus with empty subscribers."""
        self._subscribers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to.
            handler: Callback function that takes event as parameter.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug("Subscribed handler %s to event %s", handler.__name__, event_type.__name__)

    def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribed handlers.

        Args:
            event: The domain event that occurred.
        """
        event_type = type(event)

        if event_type in self._subscribers:
            logger.debug("Publishing event %s to %d handlers", event_type.__name__, len(self._subscribers[event_type]))
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error("Error handling event %s: %s", event_type.__name__, e, exc_info=True)
        else:
            logger.debug("No subscribers for event %s", event_type.__name__)
