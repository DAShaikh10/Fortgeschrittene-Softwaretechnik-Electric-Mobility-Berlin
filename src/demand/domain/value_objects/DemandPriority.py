"""
Demand Domain Value Object - DemandPriority
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.demand.domain.enums import PriorityLevel

if TYPE_CHECKING:
    from src.demand.domain.value_objects import Population, StationCount


@dataclass(frozen=True)
class DemandPriority:
    """
    Value Object representing the priority level of charging infrastructure demand.

    Business Rules:
    - Priority is calculated based on residents per station ratio
    - HIGH: > 5000 residents per station
    - MEDIUM: 2000-5000 residents per station  
    - LOW: < 2000 residents per station

    Invariants enforced to maintain validity.
    """

    level: PriorityLevel
    residents_per_station: float

    def __post_init__(self):
        """
        Validate priority on creation (invariant enforcement).
        """

        if not isinstance(self.level, PriorityLevel):
            raise ValueError("Level must be a PriorityLevel enum value")

        if self.residents_per_station < 0:
            raise ValueError("Residents per station cannot be negative")

    @staticmethod
    def calculate_priority(population: "Population", station_count: "StationCount") -> "DemandPriority":
        """
        Calculate demand priority based on population and station count ratio.

        This static factory method implements the core business logic for determining
        infrastructure demand priority. The priority classification follows industry
        best practices for EV charging infrastructure planning.

        Priority Thresholds:
            - HIGH: > 5000 residents per station (critical shortage)
            - MEDIUM: 2000-5000 residents per station (needs attention)
            - LOW: < 2000 residents per station (adequate coverage)

        Args:
            population (Population): Total population in the area (value object)
            station_count (StationCount): Number of existing charging stations (value object)

        Returns:
            DemandPriority: Calculated priority value object with level and ratio.

        Example:
            >>> priority = DemandPriority.calculate_priority(Population(15000), StationCount(3))
            >>> priority.level  # HIGH
            >>> priority.residents_per_station  # 5000.0
        """
        # Extract integer values from value objects
        pop_value = population.value
        station_value = station_count.value

        # Handle edge case: no existing stations means highest priority
        if station_value == 0:
            return DemandPriority(
                level=PriorityLevel.HIGH, residents_per_station=float(pop_value)
            )

        # Calculate the ratio of residents to available charging stations
        residents_per_station = pop_value / station_value

        # Apply business rules to determine priority level
        if residents_per_station > 5000:
            level = PriorityLevel.HIGH
        elif residents_per_station > 2000:
            level = PriorityLevel.MEDIUM
        else:
            level = PriorityLevel.LOW

        return DemandPriority(level=level, residents_per_station=residents_per_station)

    def is_high_priority(self) -> bool:
        """
        Determine if the area requires immediate infrastructure attention.

        Returns:
            bool: True if priority level is HIGH, False otherwise.
        """
        return self.level == PriorityLevel.HIGH

    def get_urgency_score(self) -> float:
        """
        Calculate numerical urgency score for resource allocation prioritization.

        The urgency score provides a quantitative measure (0-100) for ranking areas
        that need infrastructure expansion. Higher scores indicate more critical need.

        Scoring Scale:
            - 100: Critical (≥10,000 residents/station)
            - 75: High urgency (≥5,000 residents/station)
            - 50: Medium urgency (≥2,000 residents/station)
            - 25: Low urgency (<2,000 residents/station)

        Returns:
            float: Urgency score between 0 and 100.
        """
        if self.residents_per_station >= 10000:
            return 100.0  # Critical infrastructure shortage
        if self.residents_per_station >= 5000:
            return 75.0   # High demand area
        if self.residents_per_station >= 2000:
            return 50.0   # Moderate demand
        return 25.0   # Adequate coverage

    def __str__(self) -> str:
        return f"{self.level.value} ({self.residents_per_station:.0f} residents/station)"
