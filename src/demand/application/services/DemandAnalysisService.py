"""
Demand Application Service for Demand Analysis.
"""

from typing import List, Dict, Optional

from src.shared.domain.events import DomainEventBus
from src.shared.domain.value_objects import PostalCode
from src.shared.application.services import BaseService
from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.infrastructure.repositories import DemandAnalysisRepository


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
        event_bus: DomainEventBus,
    ):
        super().__init__(repository, event_bus)

    def analyze_demand(self, postal_code: str, population: int, station_count: int) -> Dict:
        """
        Use case: Analyze demand for a specific postal code area.

        Args:
            postal_code: Postal code to analyze
            population: Population in the area
            station_count: Number of charging stations

        Returns:
            Dict: Analysis results including priority and recommendations

        Raises:
            InvalidPostalCodeError: If postal code is invalid
            ValueError: If population or station count is negative
        """

        # 1. Create value objects (validation happens here)
        postal_code_vo = PostalCode(postal_code)

        # 2. Create or retrieve aggregate
        aggregate = DemandAnalysisAggregate(
            postal_code=postal_code_vo,
            population=population,
            station_count=station_count,
        )

        # 3. Calculate demand priority (generates events)
        priority = aggregate.calculate_demand_priority()

        # 4. Save aggregate
        self._repository.save(aggregate)

        # 5. Publish domain events
        self._publish_events(aggregate)

        # 6. Return analysis results
        return self._aggregate_to_dict(aggregate)

    def analyze_multiple_areas(self, areas: List[Dict[str, any]]) -> List[Dict]:
        """
        Use case: Analyze demand for multiple postal code areas.

        Args:
            areas: List of dicts with 'postal_code', 'population', 'station_count'

        Returns:
            List[Dict]: Analysis results for all areas
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
                print(f"Error analyzing {area.get('postal_code', 'unknown')}: {e}")
                continue

        return results

    def get_high_priority_areas(self) -> List[Dict]:
        """
        Use case: Get all high-priority areas requiring attention.

        Returns:
            List[Dict]: High-priority areas sorted by urgency
        """

        all_analyses = self._repository.find_all()
        high_priority = [self._aggregate_to_dict(agg) for agg in all_analyses if agg.is_high_priority()]

        # Sort by urgency score (descending)
        high_priority.sort(key=lambda x: x["urgency_score"], reverse=True)

        return high_priority

    def get_demand_analysis(self, postal_code: str) -> Optional[Dict]:
        """
        Use case: Retrieve demand analysis for a specific postal code.

        Args:
            postal_code: Postal code to retrieve

        Returns:
            Optional[Dict]: Analysis results or None if not found
        """

        postal_code_vo = PostalCode(postal_code)
        aggregate = self._repository.find_by_postal_code(postal_code_vo)

        if aggregate is None:
            return None

        return self._aggregate_to_dict(aggregate)

    def update_demand_analysis(self, postal_code: str, population: int = None, station_count: int = None) -> Dict:
        """
        Use case: Update existing demand analysis with new data.

        Args:
            postal_code: Postal code to update
            population: New population (optional)
            station_count: New station count (optional)

        Returns:
            Dict: Updated analysis results

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
        self._publish_events(aggregate)

        return self._aggregate_to_dict(aggregate)

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
            "current_stations": aggregate.station_count,
            "recommended_additional_stations": additional_stations,
            "recommended_total_stations": aggregate.station_count + additional_stations,
            "target_ratio": target_ratio,
            "current_ratio": aggregate.get_residents_per_station(),
            "coverage_assessment": aggregate.get_coverage_assessment(),
        }

    def _aggregate_to_dict(self, aggregate: DemandAnalysisAggregate) -> Dict:
        """
        Transform aggregate to dictionary for application layer.

        Args:
            aggregate: DemandAnalysisAggregate to transform

        Returns:
            Dict: Dictionary representation of the aggregate
        """

        return {
            "postal_code": aggregate.postal_code.value,
            "population": aggregate.population,
            "station_count": aggregate.station_count,
            "demand_priority": aggregate.demand_priority.level.value,
            "residents_per_station": aggregate.demand_priority.residents_per_station,
            "urgency_score": aggregate.demand_priority.get_urgency_score(),
            "is_high_priority": aggregate.is_high_priority(),
            "needs_expansion": aggregate.needs_infrastructure_expansion(),
            "coverage_assessment": aggregate.get_coverage_assessment(),
        }
