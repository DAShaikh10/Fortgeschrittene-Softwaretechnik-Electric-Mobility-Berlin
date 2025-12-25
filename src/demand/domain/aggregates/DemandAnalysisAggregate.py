"""
Demand Domain Aggregate - Demand Analysis Aggregate Module.
"""

from typing import List
from dataclasses import dataclass, field

from src.shared.domain.value_objects import PostalCode
from src.demand.domain.value_objects import DemandPriority
from src.shared.domain.events import DomainEvent
from src.demand.domain.events import (
    DemandAnalysisCalculatedEvent,
    HighDemandAreaIdentifiedEvent,
)


@dataclass
class DemandAnalysisAggregate:
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
    - Priority must be recalculated when data changes
    """

    postal_code: PostalCode  # Identity
    population: int
    station_count: int
    demand_priority: DemandPriority = None
    _domain_events: List[DomainEvent] = field(
        default_factory=list, init=False, repr=False
    )

    def __post_init__(self):
        """
        Initialize aggregate and enforce invariants.
        """

        if self.population < 0:
            raise ValueError("Population cannot be negative")

        if self.station_count < 0:
            raise ValueError("Station count cannot be negative")

        # Calculate priority if not provided
        if self.demand_priority is None:
            object.__setattr__(
                self,
                "demand_priority",
                DemandPriority.calculate_priority(self.population, self.station_count),
            )

    def calculate_demand_priority(self) -> DemandPriority:
        """
        Business logic: Calculate demand priority for this area.

        Returns:
            DemandPriority: Calculated priority
        """

        priority = DemandPriority.calculate_priority(self.population, self.station_count)
        object.__setattr__(self, "demand_priority", priority)

        # Emit domain event
        event = DemandAnalysisCalculatedEvent(
            postal_code=self.postal_code.value,
            population=self.population,
            station_count=self.station_count,
            demand_priority=priority.level.value,
            residents_per_station=priority.residents_per_station,
        )
        self._add_domain_event(event)

        # Emit high demand event if priority is high
        if priority.is_high_priority():
            high_demand_event = HighDemandAreaIdentifiedEvent(
                postal_code=self.postal_code.value,
                population=self.population,
                station_count=self.station_count,
                urgency_score=priority.get_urgency_score(),
            )
            self._add_domain_event(high_demand_event)

        return priority

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

    def _add_domain_event(self, event: DomainEvent):
        """
        Add domain event to be published.

        Args:
            event: Domain event to add
        """

        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        """
        Get all domain events generated by this aggregate.

        Returns:
            List of domain events
        """

        return self._domain_events.copy()

    def clear_domain_events(self):
        """
        Clear all domain events after they have been published.
        """

        self._domain_events.clear()

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
