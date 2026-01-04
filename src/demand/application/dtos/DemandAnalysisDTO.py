"""
Data Transfer Object for Demand Analysis information.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DemandAnalysisDTO:
    """
    DTO for transferring demand analysis data to the presentation layer.

    This prevents the UI from:
    - Calling domain methods directly on aggregates
    - Depending on aggregate structure
    - Breaking aggregate encapsulation

    Attributes:
        postal_code: The postal code value as string
        population: Population count in the area
        station_count: Number of charging stations
        demand_priority: Priority level (LOW, MEDIUM, HIGH)
        residents_per_station: Ratio of residents to stations
        urgency_score: Calculated urgency score (0.0 to 1.0)
        is_high_priority: Whether area is high priority
        needs_expansion: Whether infrastructure expansion is needed
        coverage_assessment: Coverage assessment (CRITICAL, POOR, ADEQUATE, GOOD)
    """

    postal_code: str
    population: int
    station_count: int
    demand_priority: str
    residents_per_station: float
    urgency_score: float
    is_high_priority: bool
    needs_expansion: bool
    coverage_assessment: str

    @staticmethod
    def from_aggregate(aggregate) -> "DemandAnalysisDTO":
        """
        Create DTO from aggregate.

        Args:
            aggregate: DemandAnalysisAggregate domain object

        Returns:
            DemandAnalysisDTO: Immutable data transfer object
        """
        return DemandAnalysisDTO(
            postal_code=aggregate.postal_code.value,
            population=aggregate.get_population(),
            station_count=aggregate.get_station_count(),
            demand_priority=aggregate.demand_priority.level.value,
            residents_per_station=aggregate.demand_priority.residents_per_station,
            urgency_score=aggregate.demand_priority.get_urgency_score(),
            is_high_priority=aggregate.is_high_priority(),
            needs_expansion=aggregate.needs_infrastructure_expansion(),
            coverage_assessment=aggregate.get_coverage_assessment().value,
        )
