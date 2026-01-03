"""
Shared Application Base Service
"""

from typing import Optional

from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.aggregates import BaseAggregate


class BaseService:
    """
    Base Service class for Application Services.
    """

    def __init__(self, repository, event_bus: Optional[IDomainEventPublisher] = None):
        self._repository = repository
        self._event_bus = event_bus

    @property
    def repository(self):
        """Get the repository instance."""
        return self._repository

    @property
    def event_bus(self) -> Optional[IDomainEventPublisher]:
        """Get the event bus instance."""
        return self._event_bus

    def publish_events(self, aggregate: BaseAggregate):
        """
        Publish all domain events from the aggregate.

        Args:
            aggregate (Aggregate): Aggregate with events to publish
        """

        if self._event_bus is None:
            return

        events = aggregate.get_domain_events()
        for event in events:
            self._event_bus.publish(event)

        aggregate.clear_domain_events()
