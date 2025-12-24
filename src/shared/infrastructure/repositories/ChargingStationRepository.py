"""
Shared Infrastructure Abstract Charging Station Repository Module.
"""

from typing import List
from abc import ABC, abstractmethod

from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode


class ChargingStationRepository(ABC):
    """
    Abstract base class for `ChargingStationRepository`.
    Defines the interface for accessing charging station data.
    """

    @abstractmethod
    def find_stations_by_postal_code(self, postal_code: PostalCode) -> List[ChargingStation]:
        """
        Find charging stations by postal code.

        Args:
            postal_code (PostalCode): Postal code to search for.
        Returns:
            List of ChargingStation entities found.
        """
