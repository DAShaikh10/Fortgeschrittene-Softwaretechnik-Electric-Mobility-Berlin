"""
Shared Domain - Domain Event Publisher Interface.
"""

from abc import ABC, abstractmethod
from typing import Callable, Type

from .domain_event import DomainEvent


class IDomainEventPublisher(ABC):
    """
    Interface for publishing domain events.
    """

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The type of event to subscribe to.
            handler: Callback function that takes event as parameter.
        """
        raise NotImplementedError

    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribed handlers.

        Args:
            event: The domain event that occurred.
        """
        raise NotImplementedError
