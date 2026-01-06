"""
Shared Domain PowerCapacity Value Object.
"""

from dataclasses import dataclass

from src.shared.domain.constants import PowerThresholds


@dataclass(frozen=True)
class PowerCapacity:
    """
    Value Object representing the power capacity of a charging station.

    Business Rules:
    - Power capacity must be non-negative
    - Power capacity must not exceed reasonable maximum (1000 kW)
    - Fast charging is defined as >= 50 kW

    Invariants enforced to maintain validity.
    """

    kilowatts: float

    def __post_init__(self):
        """
        Validate power capacity on creation (invariant enforcement).
        """
        if self.kilowatts < 0:
            raise ValueError("Power capacity cannot be negative")
        if self.kilowatts > PowerThresholds.MAX_REASONABLE_POWER_KW:
            raise ValueError(
                f"Power capacity exceeds maximum reasonable value ({PowerThresholds.MAX_REASONABLE_POWER_KW} kW)"
            )

    def is_fast_charging(self) -> bool:
        """
        Business rule: Determine if this is a fast charging station.

        Fast charging is defined as >= 50 kW according to industry standards.

        Returns:
            bool: True if power capacity is >= 50 kW
        """
        return self.kilowatts >= PowerThresholds.FAST_CHARGING_THRESHOLD_KW
