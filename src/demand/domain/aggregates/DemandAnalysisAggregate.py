"""
Demand Domain Aggregate - Demand Analysis Aggregate Module.
"""

from dataclasses import dataclass

from src.shared.domain.value_objects import PostalCode
from src.shared.domain.aggregates import BaseAggregate
from src.demand.domain.value_objects import DemandPriority
from src.demand.domain.events import (
    DemandAnalysisCalculatedEvent,
    HighDemandAreaIdentifiedEvent,
)


@dataclass
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
    - Population and station count must be non-negative
    - Priority must be consistent with population/station data
    """

    postal_code: PostalCode  # Identity
    population: int
    station_count: int
    demand_priority: DemandPriority

    def __post_init__(self):
        """
        Initialize aggregate and enforce invariants.
        """
        # Initialize base aggregate event handling.
        super().__init__()

        # Validate invariants.
        if self.population < 0:
            raise ValueError(f"Population cannot be negative, got: {self.population}")

        if self.station_count < 0:
            raise ValueError(f"Station count cannot be negative, got: {self.station_count}")

        if self.demand_priority is None:
            raise ValueError("Demand priority must be provided (use factory methods)")

    @staticmethod
    def create(postal_code: PostalCode, population: int, station_count: int) -> "DemandAnalysisAggregate":
        """
        Factory Method: Create a new demand analysis aggregate with calculated priority.

        Args:
            postal_code: PostalCode value object for the area
            population: Population count in the area
            station_count: Number of charging stations in the area

        Returns:
            DemandAnalysisAggregate: Newly created aggregate with calculated priority

        Raises:
            ValueError: If population or station_count is negative
            InvalidPostalCodeError: If postal code is invalid
        """
        # Calculate priority before construction.
        priority = DemandPriority.calculate_priority(population, station_count)

        # Create aggregate with all required data.
        return DemandAnalysisAggregate(
            postal_code=postal_code,
            population=population,
            station_count=station_count,
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
            population: Population count in the area
            station_count: Number of charging stations in the area
            existing_priority: Previously calculated DemandPriority

        Returns:
            DemandAnalysisAggregate: Reconstituted aggregate

        Raises:
            ValueError: If population or station_count is negative
        """
        return DemandAnalysisAggregate(
            postal_code=postal_code,
            population=population,
            station_count=station_count,
            demand_priority=existing_priority,
        )

    def calculate_demand_priority(self) -> DemandPriority:
        """
        Business logic: Calculate demand priority for this area.

        Returns:
            DemandPriority: Calculated priority
        """

        priority = DemandPriority.calculate_priority(self.population, self.station_count)
        object.__setattr__(self, "demand_priority", priority)

        # Emit domain event.
        event = DemandAnalysisCalculatedEvent(
            postal_code=self.postal_code,
            population=self.population,
            station_count=self.station_count,
            demand_priority=priority,
        )
        self._add_domain_event(event)

        # Emit high demand event if priority is high.
        if priority.is_high_priority():
            high_demand_event = HighDemandAreaIdentifiedEvent(
                postal_code=self.postal_code,
                population=self.population,
                station_count=self.station_count,
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
        return self.postal_code

    def get_population(self) -> int:
        """
        Query: Get the population count.

        Returns:
            int: Population in this area.
        """
        return self.population

    def get_station_count(self) -> int:
        """
        Query: Get the number of charging stations.

        Returns:
            int: Station count in this area.
        """
        return self.station_count

    def get_demand_priority(self) -> DemandPriority:
        """
        Query: Get the demand priority value object.

        Returns:
            DemandPriority: Current demand priority.
        """
        return self.demand_priority

    def update_population(self, new_population: int):
        """
        Business logic: Update population and recalculate priority.

        Args:
            new_population: New population value

        Raises:
            ValueError: If population is negative
        """

        if new_population < 0:
            raise ValueError("Population cannot be negative")

        object.__setattr__(self, "population", new_population)
        self.calculate_demand_priority()

    def update_station_count(self, new_count: int):
        """
        Business logic: Update station count and recalculate priority.

        Args:
            new_count: New station count

        Raises:
            ValueError: If station count is negative
        """

        if new_count < 0:
            raise ValueError("Station count cannot be negative")

        object.__setattr__(self, "station_count", new_count)
        self.calculate_demand_priority()

    def get_residents_per_station(self) -> float:
        """
        Query: Get residents per station ratio.

        Returns:
            float: Residents per station (population if no stations)
        """

        if self.station_count == 0:
            return float(self.population)
        return self.population / self.station_count

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

        return self.demand_priority.residents_per_station > 3000

    def get_coverage_assessment(self) -> str:
        """
        Business logic: Assess infrastructure coverage level.

        Returns:
            str: Coverage assessment ("CRITICAL", "POOR", "ADEQUATE", "GOOD")
        """

        ratio = self.get_residents_per_station()

        if ratio > 10000:
            return "CRITICAL"
        if ratio > 5000:
            return "POOR"
        if ratio > 2000:
            return "ADEQUATE"
        return "GOOD"

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

        recommended_total = int(self.population / target_ratio)
        additional_needed = max(0, recommended_total - self.station_count)

        return additional_needed

    def to_dict(self) -> dict:
        """
        Convert aggregate to dictionary representation for presentation layer.

        Returns:
            dict: Dictionary with aggregate data
        """
        return {
            "postal_code": self.postal_code.value,
            "population": self.population,
            "station_count": self.station_count,
            "demand_priority": self.demand_priority.level.value,
            "residents_per_station": self.demand_priority.residents_per_station,
            "urgency_score": self.demand_priority.get_urgency_score(),
            "is_high_priority": self.is_high_priority(),
            "needs_expansion": self.needs_infrastructure_expansion(),
            "coverage_assessment": self.get_coverage_assessment(),
        }
