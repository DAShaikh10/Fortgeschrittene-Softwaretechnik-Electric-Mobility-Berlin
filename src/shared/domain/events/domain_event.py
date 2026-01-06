"""
Shared Domain Event - Domain Event Module.
"""

import uuid

from datetime import datetime
from dataclasses import dataclass, field


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """
    Base class for all domain events.
    Immutable and contains metadata about when it occurred.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)

    def event_type(self):
        """
        Returns the type of the event
        """

        return self.__class__.__name__
