"""
src.shared.domain.events - Shared Kernel Domain Events module.
"""

from .domain_event import DomainEvent
from .domain_event_publisher_interface import IDomainEventPublisher
from .station_search_performed_event import StationSearchPerformedEvent
from .station_search_failed_event import StationSearchFailedEvent
from .no_stations_found_event import NoStationsFoundEvent
from .stations_found_event import StationsFoundEvent

__all__ = [
    "DomainEvent",
    "IDomainEventPublisher",
    "StationSearchPerformedEvent",
    "StationSearchFailedEvent",
    "NoStationsFoundEvent",
    "StationsFoundEvent",
]
