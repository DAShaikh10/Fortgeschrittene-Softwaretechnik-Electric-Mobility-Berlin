"""
Demand Domain Aggregate - Demand Analysis Aggregate Module.
"""

from src.shared.domain.value_objects import PostalCode
from src.shared.domain.aggregates import BaseAggregate
from src.shared.domain.enums import CoverageAssessment
from src.demand.domain.value_objects import DemandPriority, Population, StationCount
from src.demand.domain.events import (
    DemandAnalysisCalculatedEvent,
    HighDemandAreaIdentifiedEvent,
)


class DemandAnalysisAggregate(BaseAggregate):
    """
    Aggregate Root: Represents a demand analysis for a postal code area.

    Responsibilities:
    - Maintain demand analysis state
    - Calculate demand priority
    - Enforce business rules
    - Generate domain events

    Business Invariants:
    - Postal code must be valid
    - Population and station count must be non-negative (enforced by value objects)
    - Priority must be consistent with population/station data
    """

    def __init__(
        self,
        postal_code: PostalCode,
        population: Population,
        station_count: StationCount,
        demand_priority: DemandPriority,
    ):
        """
        Initialize the DemandAnalysisAggregate.

        Args:
            postal_code: Postal code identifying the area
            population: Population value object
            station_count: Station count value object
            demand_priority: Demand priority value object
        """
        # Initialize base aggregate event handling.
        super().__init__()

        # Set instance attributes
        self._postal_code = postal_code
        self._population = population
        self._station_count = station_count
        self._demand_priority = demand_priority

        # Validate invariants (value objects handle their own validation).
        if self._demand_priority is None:
            raise ValueError("Demand priority must be provided (use factory methods)")

    @property
    def postal_code(self) -> PostalCode:
        """Get the postal code."""
        return self._postal_code

    @property
    def population(self) -> Population:
        """Get the population."""
        return self._population

    @property
    def station_count(self) -> StationCount:
        """Get the station count."""
        return self._station_count

    @property
    def demand_priority(self) -> DemandPriority:
        """Get the demand priority."""
        return self._demand_priority

    @staticmethod
    def create(postal_code: PostalCode, population: int, station_count: int) -> "DemandAnalysisAggregate":
        """
        Factory Method: Create a new demand analysis aggregate with calculated priority.

        Args:
            postal_code: PostalCode value object for the area
            population: Population count in the area (will be wrapped in Population value object)
            station_count: Number of charging stations (will be wrapped in StationCount value object)

        Returns:
            DemandAnalysisAggregate: Newly created aggregate with calculated priority

        Raises:
            ValueError: If population or station_count is negative
            InvalidPostalCodeError: If postal code is invalid
        """
        # Create value objects (validation happens here)
        pop_vo = Population(population)
        station_vo = StationCount(station_count)

        # Calculate priority before construction.
        priority = DemandPriority.calculate_priority(pop_vo, station_vo)

        # Create aggregate with all required data.
        return DemandAnalysisAggregate(
            postal_code=postal_code,
            population=pop_vo,
            station_count=station_vo,
            demand_priority=priority,
        )

    @staticmethod
    def create_from_existing(
        postal_code: PostalCode, population: int, station_count: int, existing_priority: DemandPriority
    ) -> "DemandAnalysisAggregate":
        """
        Factory Method: Reconstitute an aggregate from stored data.

        Used when retrieving aggregates from repository with pre-calculated priority.
        Does not recalculate priority; uses the provided one.

        Args:
            postal_code: PostalCode value object for the area
            population: Population count (will be wrapped in Population value object)
            station_count: Station count (will be wrapped in StationCount value object)
            existing_priority: Previously calculated DemandPriority

        Returns:
            DemandAnalysisAggregate: Reconstituted aggregate

        Raises:
            ValueError: If population or station_count is negative
        """
        return DemandAnalysisAggregate(
            postal_code=postal_code,
            population=Population(population),
            station_count=StationCount(station_count),
            demand_priority=existing_priority,
        )

    def calculate_demand_priority(self) -> DemandPriority:
        """
        Business logic: Calculate demand priority for this area.

        Returns:
            DemandPriority: Calculated priority
        """

        priority = DemandPriority.calculate_priority(self._population, self._station_count)
        self._demand_priority = priority

        # Emit domain event.
        event = DemandAnalysisCalculatedEvent(
            postal_code=self._postal_code,
            population=self._population.value,
            station_count=self._station_count.value,
            demand_priority=priority,
        )
        self._add_domain_event(event)

        # Emit high demand event if priority is high.
        if priority.is_high_priority():
            high_demand_event = HighDemandAreaIdentifiedEvent(
                postal_code=self._postal_code,
                population=self._population.value,
                station_count=self._station_count.value,
                urgency_score=priority.get_urgency_score(),
            )
            self._add_domain_event(high_demand_event)

        return priority

    def get_postal_code(self) -> PostalCode:
        """
        Query: Get the postal code for this area.

        Returns:
            PostalCode: Postal code value object.
        """
        return self._postal_code

    def get_population(self) -> int:
        """
        Query: Get the population count.

        Returns:
            int: Population in this area.
        """
        return self._population.value

    def get_station_count(self) -> int:
        """
        Query: Get the number of charging stations.

        Returns:
            int: Station count in this area.
        """
        return self._station_count.value

    def get_demand_priority(self) -> DemandPriority:
        """
        Query: Get the demand priority value object.

        Returns:
            DemandPriority: Current demand priority.
        """
        return self._demand_priority

    def update_population(self, new_population: int):
        """
        Business logic: Update population and recalculate priority.

        Args:
            new_population: New population value

        Raises:
            ValueError: If population is negative
        """

        self._population = Population(new_population)
        self.calculate_demand_priority()

    def update_station_count(self, new_count: int):
        """
        Business logic: Update station count and recalculate priority.

        Args:
            new_count: New station count

        Raises:
            ValueError: If station count is negative
        """

        self._station_count = StationCount(new_count)
        self.calculate_demand_priority()

    def get_residents_per_station(self) -> float:
        """
        Query: Get residents per station ratio.

        Returns:
            float: Residents per station (population if no stations)
        """

        if self._station_count.is_zero():
            return float(self._population.value)
        return self._population.value / self._station_count.value

    def is_high_priority(self) -> bool:
        """
        Business rule: Check if this area is high priority.

        Returns:
            bool: True if high priority
        """

        return self.demand_priority.is_high_priority()

    def needs_infrastructure_expansion(self) -> bool:
        """
        Business rule: Determine if area needs more charging stations.

        Returns:
            bool: True if expansion is needed
        """

        return self._demand_priority.residents_per_station > 3000

    def get_coverage_assessment(self) -> CoverageAssessment:
        """
        Business logic: Assess infrastructure coverage level.

        Returns:
            CoverageAssessment: Coverage assessment
        """

        ratio = self.get_residents_per_station()

        if ratio > 10000:
            return CoverageAssessment.CRITICAL
        if ratio > 5000:
            return CoverageAssessment.POOR
        if ratio > 2000:
            return CoverageAssessment.ADEQUATE
        return CoverageAssessment.GOOD

    def calculate_recommended_stations(self, target_ratio: float = 2000.0) -> int:
        """
        Business logic: Calculate recommended number of stations to meet target ratio.

        Args:
            target_ratio: Target residents per station (default: 2000)

        Returns:
            int: Recommended number of additional stations needed
        """

        if target_ratio <= 0:
            raise ValueError("Target ratio must be positive")

        recommended_total = int(self._population.value / target_ratio)
        additional_needed = max(0, recommended_total - self._station_count.value)
        return additional_needed
