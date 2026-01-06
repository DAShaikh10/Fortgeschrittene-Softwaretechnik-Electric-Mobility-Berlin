"""
Data Transfer Object for Power Capacity information.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class PowerCapacityDTO:
    """
    DTO for transferring power capacity data to the presentation layer.

    This prevents the UI from:
    - Depending on infrastructure types (pandas DataFrame)
    - Breaking application layer encapsulation
    - Violating Dependency Inversion Principle

    Attributes:
        postal_code: The postal code value as string
        total_capacity_kw: Total power capacity in kilowatts
        station_count: Number of charging stations
        capacity_category: Optional category classification (None, 'Low', 'Medium', 'High', 'None')
    """

    postal_code: str
    total_capacity_kw: float
    station_count: int
    capacity_category: Optional[str] = None

    def to_dict(self) -> dict:
        """
        Convert DTO to a plain dictionary for UI/dataframe consumption.

        Returns:
            dict: Dictionary representation of the DTO.
        """
        result = {
            "postal_code": self.postal_code,
            "total_capacity_kw": self.total_capacity_kw,
            "station_count": self.station_count,
        }
        if self.capacity_category is not None:
            result["capacity_category"] = self.capacity_category
        return result
