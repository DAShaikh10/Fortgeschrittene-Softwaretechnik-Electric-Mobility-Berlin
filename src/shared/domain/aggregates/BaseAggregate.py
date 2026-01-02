"""
Shared Domain Aggregate - Base Aggregate Module.
"""

from typing import List

from src.shared.domain.events import DomainEvent


class BaseAggregate:
    """
    Base Aggregate Root: Provides common event handling for all aggregates.
    """

    def __init__(self):
        """
        Initialize the base aggregate with empty event list.
        """
        self._domain_events: List[DomainEvent] = []

    def _add_domain_event(self, event: DomainEvent):
        """
        Add a domain event to be published.

        Args:
            event: Domain event to add to the event list.
        """
        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """
        Return collected domain events.

        Returns:
            List[DomainEvent]: Copy of domain events list.
        """
        return self._domain_events.copy()

    def clear_domain_events(self):
        """
        Clear events after publishing.

        Should be called after all events have been published to the event bus.
        """
        self._domain_events.clear()

    def has_domain_events(self) -> bool:
        """
        Check if aggregate has pending domain events.

        Returns:
            bool: True if there are domain events to publish.
        """
        return len(self._domain_events) > 0

    def get_event_count(self) -> int:
        """
        Get the number of pending domain events.

        Returns:
            int: Number of domain events waiting to be published.
        """
        return len(self._domain_events)
