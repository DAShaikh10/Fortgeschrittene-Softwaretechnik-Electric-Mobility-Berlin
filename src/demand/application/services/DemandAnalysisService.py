"""
Demand Application Service for Demand Analysis.
"""

from typing import Any, Dict, List, Optional

from src.shared.infrastructure.logging_config import get_logger

from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.value_objects import PostalCode
from src.shared.application.services import BaseService
from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.infrastructure.repositories import DemandAnalysisRepository
from src.demand.application.dto import DemandAnalysisDTO

logger = get_logger(__name__)


class DemandAnalysisService(BaseService):
    """
    Application Service for calculating charging infrastructure demand.

    Coordinates workflow:
    1. Create/update DemandAnalysis aggregate
    2. Calculate priority
    3. Publish events
    4. Return analysis results

    Responsibilities:
    - Orchestrate use cases
    - Coordinate with repository
    - Publish domain events
    - Transform between domain and application layers
    """

    def __init__(
        self,
        repository: DemandAnalysisRepository,
        event_bus: IDomainEventPublisher,
    ):
        super().__init__(repository, event_bus)

    def analyze_demand(self, postal_code: str, population: int, station_count: int) -> DemandAnalysisDTO:
        """
        Use case: Analyze demand for a specific postal code area.

        Args:
            postal_code: Postal code to analyze
            population: Population in the area
            station_count: Number of charging stations

        Returns:
            DemandAnalysisDTO: DTO with demand analysis results

        Raises:
            InvalidPostalCodeError: If postal code is invalid
            ValueError: If population or station count is negative
        """

        # Create value objects (validation happens here)
        postal_code_vo = PostalCode(postal_code)

        # Create aggregate using factory method (priority calculated automatically)
        aggregate = DemandAnalysisAggregate.create(
            postal_code=postal_code_vo,
            population=population,
            station_count=station_count,
        )

        # Calculate demand priority (generates events)
        aggregate.calculate_demand_priority()

        self._repository.save(aggregate)

        self.publish_events(aggregate)

        return self._to_dto(aggregate)

    def analyze_multiple_areas(self, areas: List[Dict[str, Any]]) -> List[DemandAnalysisDTO]:
        """
        Use case: Analyze demand for multiple postal code areas.

        Args:
            areas: List of dicts with 'postal_code', 'population', 'station_count'

        Returns:
            List[DemandAnalysisDTO]: Analysis results for all areas
        """

        results = []
        for area in areas:
            try:
                result = self.analyze_demand(
                    postal_code=area["postal_code"],
                    population=area["population"],
                    station_count=area["station_count"],
                )
                results.append(result)
            except Exception as e:
                # Log error but continue processing other areas
                logger.error("Error analyzing %s: %s", area.get("postal_code", "unknown"), e, exc_info=True)
                continue

        return results

    def get_high_priority_areas(self) -> List[DemandAnalysisDTO]:
        """
        Use case: Get all high-priority areas requiring attention.

        Returns:
            List[DemandAnalysisDTO]: High-priority areas sorted by urgency
        """

        all_analyses = self._repository.find_all()
        high_priority = [agg for agg in all_analyses if agg.is_high_priority()]

        # Sort by urgency score (descending)
        high_priority.sort(key=lambda x: x.demand_priority.get_urgency_score(), reverse=True)

        return [self._to_dto(agg) for agg in high_priority]

    def get_demand_analysis(self, postal_code: str) -> Optional[DemandAnalysisDTO]:
        """
        Use case: Retrieve demand analysis for a specific postal code.

        Args:
            postal_code: Postal code to retrieve

        Returns:
            Optional[DemandAnalysisDTO]: Analysis DTO or None if not found
        """

        postal_code_vo = PostalCode(postal_code)
        aggregate = self._repository.find_by_postal_code(postal_code_vo)

        if aggregate is None:
            return None

        return self._to_dto(aggregate)

    def update_demand_analysis(
        self, postal_code: str, population: int = None, station_count: int = None
    ) -> DemandAnalysisDTO:
        """
        Use case: Update existing demand analysis with new data.

        Args:
            postal_code: Postal code to update
            population: New population (optional)
            station_count: New station count (optional)

        Returns:
            DemandAnalysisDTO: Updated analysis DTO

        Raises:
            ValueError: If analysis not found or invalid parameters
        """
        postal_code_vo = PostalCode(postal_code)
        aggregate = self._repository.find_by_postal_code(postal_code_vo)

        if aggregate is None:
            raise ValueError(f"No analysis found for postal code: {postal_code}")

        # Update data
        if population is not None:
            aggregate.update_population(population)

        if station_count is not None:
            aggregate.update_station_count(station_count)

        # Save updated aggregate
        self._repository.save(aggregate)

        # Publish events
        self.publish_events(aggregate)

        return self._to_dto(aggregate)

    def _to_dto(self, aggregate: DemandAnalysisAggregate) -> DemandAnalysisDTO:
        """Map a domain aggregate to an application DTO."""
        return DemandAnalysisDTO.from_aggregate(aggregate)

    def get_recommendations(self, postal_code: str, target_ratio: float = 2000.0) -> Dict:
        """
        Use case: Get infrastructure recommendations for an area.

        Args:
            postal_code: Postal code to analyze
            target_ratio: Target residents per station ratio

        Returns:
            Dict: Recommendations including needed stations
        """

        postal_code_vo = PostalCode(postal_code)
        aggregate = self._repository.find_by_postal_code(postal_code_vo)

        if aggregate is None:
            raise ValueError(f"No analysis found for postal code: {postal_code}")

        additional_stations = aggregate.calculate_recommended_stations(target_ratio)

        return {
            "postal_code": postal_code,
            "current_stations": aggregate.get_station_count(),
            "recommended_additional_stations": additional_stations,
            "recommended_total_stations": aggregate.get_station_count() + additional_stations,
            "target_ratio": target_ratio,
            "current_ratio": aggregate.get_residents_per_station(),
            "coverage_assessment": aggregate.get_coverage_assessment().value,
        }
