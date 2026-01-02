"""
Demand Application Event Handler - High Demand Area Identified.
"""

from src.shared.infrastructure.logging_config import get_logger

from src.demand.domain.events import HighDemandAreaIdentifiedEvent

logger = get_logger(__name__)


class HighDemandAreaEventHandler:
    """
    Handler for HighDemandAreaIdentifiedEvent.

    Note: This is an INTEGRATION EVENT that may trigger
    actions across bounded contexts or external systems.
    """

    @staticmethod
    def handle(event: HighDemandAreaIdentifiedEvent) -> None:
        """
        Handle high demand area identified event.

        Args:
            event: The HighDemandAreaIdentifiedEvent instance.
        """
        logger.warning(
            "[EVENT] HIGH DEMAND AREA IDENTIFIED: Postal Code %s | "
            "Urgency Score: %.2f | Population: %d | Stations: %d",
            event.postal_code,
            event.urgency_score,
            event.population,
            event.station_count,
        )
