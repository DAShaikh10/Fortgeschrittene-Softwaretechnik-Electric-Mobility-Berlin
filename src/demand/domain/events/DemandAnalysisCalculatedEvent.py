"""
Demand Domain Event: Demand Analysis Calculated.
"""

from dataclasses import dataclass

from src.shared.domain.events import DomainEvent


@dataclass(frozen=True)
class DemandAnalysisCalculatedEvent(DomainEvent):
    """
    Domain Event: Demand analysis calculation is completed.

    Emitted by: DemandAnalysisAggregate.calculate_demand_priority()
    Consumed by:
        - DemandAnalysisEventHandler (logging/auditing)
        - Report generators
        - UI dashboards

    This is a pure data class representing something that happened in the domain.
    Event handlers are in the application layer (event_handlers/).
    """

    postal_code: str
    population: int
    station_count: int
    demand_priority: str  # "High", "Medium", "Low"
    residents_per_station: float
