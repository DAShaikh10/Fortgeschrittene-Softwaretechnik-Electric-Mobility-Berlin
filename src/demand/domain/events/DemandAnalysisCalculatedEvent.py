"""
Demand Domain Event: Demand Analysis Calculated.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.shared.domain.events import DomainEvent

if TYPE_CHECKING:
    from src.shared.domain.value_objects import PostalCode
    from src.demand.domain.value_objects import DemandPriority


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

    Uses rich domain types instead of primitives for type safety and domain integrity.
    """

    postal_code: "PostalCode"
    population: int
    station_count: int
    demand_priority: "DemandPriority"
