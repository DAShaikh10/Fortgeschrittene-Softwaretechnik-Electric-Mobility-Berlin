"""
Demand Domain Event - High Demand Area Identified Event
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.shared.domain.events import DomainEvent

if TYPE_CHECKING:
    from src.shared.domain.value_objects import PostalCode


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

    Uses rich domain types instead of primitives for type safety and domain integrity.
    """

    postal_code: "PostalCode"
    population: int
    station_count: int
    urgency_score: float
