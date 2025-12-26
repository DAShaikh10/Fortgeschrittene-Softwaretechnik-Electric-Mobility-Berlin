"""
Demand Domain Event: Demand Analysis Calculated.
"""

from dataclasses import dataclass

from src.shared.domain.events import DomainEvent
from src.shared.infrastructure.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class DemandAnalysisCalculatedEvent(DomainEvent):
    """
    Emitted when: Demand analysis calculation is completed.
    Emitted by: DemandAnalysisService (Application Layer).
    Consumed by: UI (display analysis), Report generator.
    """

    postal_code: str
    population: int
    station_count: int
    demand_priority: str  # "High", "Medium", "Low"
    residents_per_station: float

    @staticmethod
    def log_demand_calculation(event: "DemandAnalysisCalculatedEvent"):
        """
        Log the demand analysis calculated event.

        Args:
            event (DemandAnalysisCalculatedEvent): The event instance to log.
        """

        logger.info(
            "[EVENT] - DemandAnalysisCalculatedEvent - Demand analysis calculated for postal code: %s",
            event.postal_code,
        )
