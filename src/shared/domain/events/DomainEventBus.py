"""
Shared Domain Event Bus Module.
"""

from typing import Callable, Dict, List, Type

from src.shared.infrastructure.logging_config import get_logger

from .DomainEvent import DomainEvent

logger = get_logger(__name__)


class DomainEventBus:
    """
    Simple in-memory Domain Event Bus for publishing and subscribing to domain events.
    """

    def __init__(self):
        self._subscribers: Dict[Type[DomainEvent], List[Callable]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]):
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

    def publish(self, event: DomainEvent):
        """
        Publish an event to all subscribed handlers

        Args:
            event: The domain event that occurred
        """
        event_type = type(event)

        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error("Error handling event %s: %s", event_type.__name__, e, exc_info=True)


# Singleton instance for application-wide event bus.
_event_bus_instance = None


def get_event_bus() -> DomainEventBus:
    """
    Get the singleton event bus instance
    """

    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = DomainEventBus()

    return _event_bus_instance
