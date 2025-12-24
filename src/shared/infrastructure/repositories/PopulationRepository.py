"""
Shared Infrastructure - Population Repository Interface
"""

from typing import List
from abc import ABC, abstractmethod

from src.shared.domain.value_objects import PostalCode


class PopulationRepository(ABC):
    """
    Abstract base class for PopulationRepository.
    This repository provides residents / population data for postal codes.
    """

    @abstractmethod
    def get_all_postal_codes(self) -> List[PostalCode]:
        """
        Get all postal codes with population data.

        Returns:
            List of PostalCode value objects
        """
