"""
Shared Domain Aggregate - Base Aggregate Module.
"""

from typing import List
from dataclasses import dataclass

from src.shared.domain.events import DomainEvent


@dataclass
class BaseAggregate:
    """
    Base Aggregate Root: Represents a generic aggregate.
    """

    def __init__(self):
        self._domain_events: List[DomainEvent] = []

    def get_domain_events(self) -> List[DomainEvent]:
        """
        Return collected domain events.

        Returns:
            List[DomainEvent]: List of domain events.
        """

        return self._domain_events.copy()

    def clear_domain_events(self):
        """
        Clear events after publishing.
        """

        self._domain_events.clear()
