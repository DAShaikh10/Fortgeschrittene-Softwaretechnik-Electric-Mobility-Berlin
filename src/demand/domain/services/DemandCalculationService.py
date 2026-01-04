"""
Domain Service for Regional Demand Calculations.

This service coordinates demand calculations across multiple aggregates,
implementing business logic that doesn't naturally belong to a single aggregate.
"""

from typing import Dict, List

from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.domain.enums import PriorityLevel


class RegionalDemandAnalysis:
    """
    Value object representing regional demand analysis results.

    This encapsulates the results of analyzing multiple postal code areas together.
    """

    def __init__(
        self,
        total_population: int,
        total_stations: int,
        high_priority_count: int,
        medium_priority_count: int,
        low_priority_count: int,
        average_residents_per_station: float,
        critical_areas: List[str],
    ):
        """
        Initialize regional demand analysis.

        Args:
            total_population: Total population across all areas
            total_stations: Total stations across all areas
            high_priority_count: Number of high-priority areas
            medium_priority_count: Number of medium-priority areas
            low_priority_count: Number of low-priority areas
            average_residents_per_station: Average ratio across region
            critical_areas: List of postal codes with critical demand
        """
        self.total_population = total_population
        self.total_stations = total_stations
        self.high_priority_count = high_priority_count
        self.medium_priority_count = medium_priority_count
        self.low_priority_count = low_priority_count
        self.average_residents_per_station = average_residents_per_station
        self.critical_areas = critical_areas

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "total_population": self.total_population,
            "total_stations": self.total_stations,
            "high_priority_count": self.high_priority_count,
            "medium_priority_count": self.medium_priority_count,
            "low_priority_count": self.low_priority_count,
            "average_residents_per_station": self.average_residents_per_station,
            "critical_areas": self.critical_areas,
        }


class DemandCalculationService:
    """
    Domain Service: Coordinates demand calculations across aggregates.

    Use when logic involves multiple aggregates or doesn't fit in one aggregate.
    This service implements business rules that span multiple postal code areas.
    """

    @staticmethod
    def calculate_regional_demand(
        aggregates: List[DemandAnalysisAggregate],
    ) -> RegionalDemandAnalysis:
        """
        Calculate regional demand metrics across multiple postal code areas.

        This method implements business logic that requires analyzing multiple
        aggregates together, which doesn't naturally belong to a single aggregate.

        Args:
            aggregates: List of DemandAnalysisAggregate instances to analyze

        Returns:
            RegionalDemandAnalysis: Aggregated regional demand metrics

        Raises:
            ValueError: If aggregates list is empty
        """
        if not aggregates:
            raise ValueError("Cannot calculate regional demand from empty aggregates list")

        # Aggregate metrics across all areas
        total_population = sum(agg.get_population() for agg in aggregates)
        total_stations = sum(agg.get_station_count() for agg in aggregates)

        # Count priority levels
        high_priority_count = sum(1 for agg in aggregates if agg.get_demand_priority().is_high_priority())
        medium_priority_count = sum(
            1
            for agg in aggregates
            if agg.get_demand_priority().level == PriorityLevel.MEDIUM
        )
        low_priority_count = sum(
            1
            for agg in aggregates
            if agg.get_demand_priority().level == PriorityLevel.LOW
        )

        # Calculate average residents per station across region
        average_residents_per_station = (
            total_population / total_stations if total_stations > 0 else float("inf")
        )

        # Identify critical areas (high priority with urgency score > 0.8)
        critical_areas = [
            agg.get_postal_code().value
            for agg in aggregates
            if agg.get_demand_priority().is_high_priority()
            and agg.get_demand_priority().get_urgency_score() > 0.8
        ]

        return RegionalDemandAnalysis(
            total_population=total_population,
            total_stations=total_stations,
            high_priority_count=high_priority_count,
            medium_priority_count=medium_priority_count,
            low_priority_count=low_priority_count,
            average_residents_per_station=average_residents_per_station,
            critical_areas=critical_areas,
        )

    @staticmethod
    def compare_areas(
        aggregate1: DemandAnalysisAggregate, aggregate2: DemandAnalysisAggregate
    ) -> Dict[str, any]:
        """
        Compare demand between two postal code areas.

        This implements business logic for comparing infrastructure needs
        across different areas, which requires access to multiple aggregates.

        Args:
            aggregate1: First area to compare
            aggregate2: Second area to compare

        Returns:
            Dict with comparison metrics
        """
        priority1 = aggregate1.get_demand_priority()
        priority2 = aggregate2.get_demand_priority()

        urgency1 = priority1.get_urgency_score()
        urgency2 = priority2.get_urgency_score()

        return {
            "area1": {
                "postal_code": aggregate1.get_postal_code().value,
                "priority": priority1.level.value,
                "urgency_score": urgency1,
                "residents_per_station": priority1.residents_per_station,
            },
            "area2": {
                "postal_code": aggregate2.get_postal_code().value,
                "priority": priority2.level.value,
                "urgency_score": urgency2,
                "residents_per_station": priority2.residents_per_station,
            },
            "more_urgent": (
                aggregate1.get_postal_code().value
                if urgency1 > urgency2
                else aggregate2.get_postal_code().value
            ),
            "priority_difference": abs(urgency1 - urgency2),
        }

    @staticmethod
    def identify_priority_clusters(
        aggregates: List[DemandAnalysisAggregate],
    ) -> Dict[str, List[str]]:
        """
        Group postal code areas by priority level.

        This business logic requires analyzing multiple aggregates to identify
        patterns and clusters, which doesn't belong to a single aggregate.

        Args:
            aggregates: List of aggregates to analyze

        Returns:
            Dict mapping priority level to list of postal codes
        """
        clusters = {"High": [], "Medium": [], "Low": []}

        for agg in aggregates:
            priority_level = agg.get_demand_priority().level.value
            postal_code = agg.get_postal_code().value
            clusters[priority_level].append(postal_code)

        return clusters
