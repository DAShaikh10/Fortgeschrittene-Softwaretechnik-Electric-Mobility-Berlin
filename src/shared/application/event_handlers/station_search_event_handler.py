"""
Shared Application Event Handler - Station Search Events.
"""

from src.shared.infrastructure.logging_config import get_logger

from src.shared.domain.events import (
    StationSearchPerformedEvent,
    StationSearchFailedEvent,
    NoStationsFoundEvent,
    StationsFoundEvent,
)

logger = get_logger(__name__)


class StationSearchEventHandler:
    """
    Handler for station search events.

    Responsibilities:
    - Log search operations for auditing
    - Log search failures for debugging and monitoring
    - Log searches with no results for coverage gap analysis
    """

    @staticmethod
    def handle(event: StationSearchPerformedEvent) -> None:
        """
        Handle station search performed event.

        Args:
            event: The StationSearchPerformedEvent instance.
        """
        logger.info(
            "[EVENT] Station search performed for postal code: %s (found %d stations)",
            event.postal_code.value,
            event.stations_found,
        )

    @staticmethod
    def handle_failure(event: StationSearchFailedEvent) -> None:
        """
        Handle station search failed event.

        Args:
            event: The StationSearchFailedEvent instance.
        """
        logger.error(
            "[EVENT] Station search failed for postal code: %s - Error: %s (Type: %s)",
            event.postal_code.value,
            event.error_message,
            event.error_type or "Unknown",
        )

    @staticmethod
    def handle_no_results(event: NoStationsFoundEvent) -> None:
        """
        Handle no stations found event.

        Args:
            event: The NoStationsFoundEvent instance.
        """
        logger.warning(
            "[EVENT] No stations found for postal code: %s - Infrastructure gap identified",
            event.postal_code.value,
        )

    @staticmethod
    def handle_stations_found(event: StationsFoundEvent) -> None:
        """
        Handle stations found event.

        Args:
            event: The StationsFoundEvent instance.
        """
        logger.info(
            "[EVENT] Stations found for postal code: %s (%d stations discovered)",
            event.postal_code.value,
            event.stations_found,
        )
