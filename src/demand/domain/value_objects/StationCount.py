"""
Demand Domain Value Object - StationCount
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StationCount:
    """
    Value Object representing the number of charging stations in an area.

    Business Rules:
    - Station count must be non-negative (zero or positive)
    - Zero stations indicates no infrastructure (critical shortage)

    Invariants enforced to maintain validity.
    """

    value: int

    def __post_init__(self):
        """
        Validate station count on creation (invariant enforcement).
        """
        if not isinstance(self.value, int):
            raise TypeError("Station count must be an integer")

        if self.value < 0:
            raise ValueError(f"Station count cannot be negative, got: {self.value}")

    def __int__(self) -> int:
        """
        Allow conversion to int for calculations.
        
        Returns:
            int: Station count value
        """
        return self.value

    def is_zero(self) -> bool:
        """
        Check if there are no stations (critical shortage indicator).
        
        Returns:
            bool: True if no stations exist
        """
        return self.value == 0

    def __str__(self) -> str:
        """
        String representation.
        
        Returns:
            str: Station count value as string
        """
        return str(self.value)

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        
        Returns:
            str: StationCount representation
        """
        return f"StationCount({self.value})"
