"""
Shared Application Event Handler - Station Search Performed.
"""

from src.shared.infrastructure.logging_config import get_logger

from src.shared.domain.events import StationSearchPerformedEvent

logger = get_logger(__name__)


class StationSearchEventHandler:
    """
    Handler for StationSearchPerformedEvent.

    Responsibilities:
    - Log search operations for auditing
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
