"""
Demand Domain Event - High Demand Area Identified Event
"""

from dataclasses import dataclass

from src.shared.domain.events import DomainEvent


@dataclass(frozen=True)
class HighDemandAreaIdentifiedEvent(DomainEvent):
    """
    Emitted when: Area with high demand is identified.
    Emitted by: DemandAnalysisService.
    Consumed by: Alert service, recommendation engine.

    This is an INTEGRATION EVENT that could trigger actions in other systems.
    """

    postal_code: str
    population: int
    station_count: int
    urgency_score: float

    @staticmethod
    def log_high_demand_area(event: "HighDemandAreaIdentifiedEvent"):
        """
        Log the high demand area identified event.

        Args:
            event (HighDemandAreaIdentifiedEvent): The event instance to log.
        """

        print(f"[EVENT] High demand area identified: {event.postal_code} (Urgency Score: {event.urgency_score})")
