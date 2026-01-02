"""
Demand Domain Event - High Demand Area Identified Event
"""

from dataclasses import dataclass

from src.shared.domain.events import DomainEvent


@dataclass(frozen=True)
class HighDemandAreaIdentifiedEvent(DomainEvent):
    """
    Domain Event: Area with high charging demand is identified.

    Emitted by: DemandAnalysisAggregate.calculate_demand_priority()
    Consumed by:
        - HighDemandAreaEventHandler (alerting/logging)
        - Recommendation engine
        - External city planning systems

    This is an INTEGRATION EVENT that may trigger actions across
    bounded contexts or in external systems.

    This is a pure data class representing something that happened in the domain.
    Event handlers are in the application layer (event_handlers/).
    """

    postal_code: str
    population: int
    station_count: int
    urgency_score: float
