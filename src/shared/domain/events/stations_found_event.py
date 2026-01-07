"""
Shared Domain Event - Stations Found Event
"""

from dataclasses import dataclass

from src.shared.domain.value_objects import PostalCode

from .domain_event import DomainEvent


@dataclass(frozen=True)
class StationsFoundEvent(DomainEvent):
    """
    Domain Event: Search completed successfully and found stations.

    Emitted by: ChargingStationService (Application Layer)
    Consumed by:
        - StationSearchEventHandler (logging/tracking)
        - Analytics service (usage tracking)
        - UI (display results)
        - Monitoring systems (success rate tracking)

    This event represents a successful search operation that found one or more stations.
    """

    postal_code: PostalCode
    stations_found: int
