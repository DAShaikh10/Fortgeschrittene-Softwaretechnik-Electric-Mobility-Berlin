"""
Demand Domain Value Object - Population
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Population:
    """
    Value Object representing population count for an area.

    Business Rules:
    - Population must be non-negative (zero or positive)

    Invariants enforced to maintain validity.
    """

    value: int

    def __post_init__(self):
        """
        Validate population on creation (invariant enforcement).
        """
        if not isinstance(self.value, int):
            raise TypeError("Population must be an integer")

        if self.value < 0:
            raise ValueError(f"Population cannot be negative, got: {self.value}")

    def __int__(self) -> int:
        """
        Allow conversion to int for calculations.
        
        Returns:
            int: Population value
        """
        return self.value

    def __str__(self) -> str:
        """
        String representation.
        
        Returns:
            str: Population value as string
        """
        return str(self.value)

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        
        Returns:
            str: Population representation
        """
        return f"Population({self.value})"
