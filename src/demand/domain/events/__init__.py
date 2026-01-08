"""
src.demand.domain.events - Demand Analysis specific Domain Events module.
"""

from .demand_analysis_calculated_event import DemandAnalysisCalculatedEvent
from .high_demand_area_identified_event import HighDemandAreaIdentifiedEvent

__all__ = [
    "DemandAnalysisCalculatedEvent",
    "HighDemandAreaIdentifiedEvent",
]
