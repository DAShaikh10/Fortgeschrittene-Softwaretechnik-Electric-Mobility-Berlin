"""
Shared Domain Event - Station Search Performed Event
"""

from typing import Dict
from dataclasses import dataclass, field

from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.logging_config import get_logger

from .DomainEvent import DomainEvent

logger = get_logger(__name__)


@dataclass(frozen=True)
class StationSearchPerformedEvent(DomainEvent):
    """
    Emitted when: Search for charging stations is performed.
    Emitted by: StationSearchService (Application Layer).
    Consumed by: UI (display results), Analytics (track usage).
    """

    postal_code: PostalCode
    stations_found: int
    search_parameters: Dict[str, PostalCode] = field(default_factory=dict)

    @staticmethod
    def log_station_search(event: "StationSearchPerformedEvent"):
        """
        Log the station search performed event.

        Args:
            event (StationSearchPerformedEvent): The event instance to log.
        """

        logger.info(
            "[EVENT] - StationSearchPerformedEvent - Station search performed for postal code: %s",
            event.postal_code.value,
        )
