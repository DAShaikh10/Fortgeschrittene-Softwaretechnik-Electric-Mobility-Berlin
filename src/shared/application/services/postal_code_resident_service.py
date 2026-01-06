"""
Shared Application Service for Postal Code Resident Data.
"""

from typing import List

from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.value_objects import PostalCode, PopulationData
from src.shared.infrastructure.repositories import PopulationRepository

from .base_service import BaseService


class PostalCodeResidentService(BaseService):
    """
    Application service for managing postal code resident data.
    """

    def __init__(self, repository: PopulationRepository, event_bus: IDomainEventPublisher):
        super().__init__(repository)

        self._event_bus = event_bus

    def get_all_postal_codes(self, sort: bool = False) -> List[PostalCode]:
        """
        Get all postal codes with resident data.

        Args:
            sort (bool): Whether to return the postal codes sorted.

        Returns:
            List of PostalCode value objects.
        """

        postal_codes: List[PostalCode] = self._repository.get_all_postal_codes()
        if sort:
            postal_codes.sort(key=lambda plz: plz.value)

        return postal_codes

    def get_resident_data(self, postal_code: PostalCode) -> PopulationData:
        """
        Retrieve population data for a specific postal code area.

        Returns a PopulationData value object containing the population count
        along with helper methods for density categorization and demand calculations.

        Args:
            postal_code (PostalCode): The postal code to get resident data for.

        Returns:
            PopulationData: Immutable value object with population data and business logic.
        """
        residents_count: int = self._repository.get_residents_count(postal_code)

        population_data = PopulationData(postal_code=postal_code, population=residents_count)

        return population_data
