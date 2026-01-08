"""
Demand Application Event Handler - Demand Analysis Calculated.
"""

from src.shared.infrastructure import get_logger

from src.demand.domain.events import DemandAnalysisCalculatedEvent

logger = get_logger(__name__)


class DemandAnalysisEventHandler:
    """
    Handler for DemandAnalysisCalculatedEvent.
    """

    @staticmethod
    def handle(event: DemandAnalysisCalculatedEvent) -> None:
        """
        Handle demand analysis calculated event.

        Args:
            event: The DemandAnalysisCalculatedEvent instance.
        """
        logger.info(
            "[EVENT] Demand analysis calculated for postal code: %s | "
            "Priority: %s | Population: %d | Stations: %d | Residents/Station: %.1f",
            event.postal_code.value,
            event.demand_priority.level.value,
            event.population,
            event.station_count,
            event.demand_priority.residents_per_station,
        )
