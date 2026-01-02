"""
Shared Domain Event - Station Search Performed Event
"""

from typing import Dict
from dataclasses import dataclass, field

from src.shared.domain.value_objects import PostalCode

from .DomainEvent import DomainEvent


@dataclass(frozen=True)
class StationSearchPerformedEvent(DomainEvent):
    """
    Domain Event: Search for charging stations is performed.

    Emitted by: ChargingStationService (Application Layer)
    Consumed by:
        - StationSearchEventHandler (logging/auditing)
        - Analytics service (usage tracking)
        - UI (display results)

    This is a pure data class representing something that happened in the domain.
    Event handlers are in the application layer (event_handlers/).
    """

    postal_code: PostalCode
    stations_found: int
    search_parameters: Dict[str, PostalCode] = field(default_factory=dict)
