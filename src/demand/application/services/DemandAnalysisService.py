"""
Demand Application Service for Demand Analysis.
"""

from src.shared.domain.events import DomainEventBus
from src.demand.infrastructure.repositories import DemandAnalysisRepository


class DemandAnalysisService:
    """
    Application Service for calculating charging infrastructure demand.

    Coordinates workflow:
    1. Create/update DemandAnalysis aggregate
    2. Calculate priority
    3. Publish events
    4. Return analysis results
    """

    def __init__(
        self,
        repository: DemandAnalysisRepository,
        event_bus: DomainEventBus,
    ):
        self._repository = repository
        self._event_bus = event_bus
