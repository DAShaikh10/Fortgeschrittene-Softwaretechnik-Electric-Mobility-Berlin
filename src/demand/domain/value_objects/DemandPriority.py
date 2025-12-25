"""
Demand Domain Value Object - DemandPriority
"""

from dataclasses import dataclass
from enum import Enum


class PriorityLevel(Enum):
    """
    Enumeration for demand priority levels.
    """

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


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
    def calculate_priority(population: int, station_count: int) -> "DemandPriority":
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
            population (int): Total population in the area.
            station_count (int): Number of existing charging stations.

        Returns:
            DemandPriority: Calculated priority value object with level and ratio.

        Example:
            >>> priority = DemandPriority.calculate_priority(15000, 3)
            >>> priority.level  # HIGH
            >>> priority.residents_per_station  # 5000.0
        """
        # Handle edge case: no existing stations means highest priority
        if station_count == 0:
            return DemandPriority(
                level=PriorityLevel.HIGH, residents_per_station=float(population)
            )

        # Calculate the ratio of residents to available charging stations
        residents_per_station = population / station_count

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
