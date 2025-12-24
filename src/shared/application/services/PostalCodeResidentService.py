"""
Shared Application Service for Postal Code Resident Data.
"""

from typing import List

from src.shared.domain.events import DomainEventBus
from src.shared.domain.value_objects import PostalCode
from src.shared.domain.aggregates import ResidentDataAggregate
from src.shared.infrastructure.repositories import PopulationRepository

from .BaseService import BaseService


class PostalCodeResidentService(BaseService):
    """
    Application service for managing postal code resident data.
    """

    def __init__(self, repository: PopulationRepository, event_bus: DomainEventBus):
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

        postal_codes: List[PostalCode] = self.repository.get_all_postal_codes()
        if sort:
            postal_codes.sort(key=lambda plz: plz.value)

        # TODO: Maybe create a DTO for this?
        return postal_codes

    def get_resident_data(self, postal_code: PostalCode) -> ResidentDataAggregate:
        """
        Returns ResidentData aggregate with business logic

        Args:
            postal_code (PostalCode): The postal code to get resident data for.

        Returns:
            ResidentDataAggregate: The resident data aggregate for the given postal code.
        """
        residents_count: int = self.repository.get_residents_count(postal_code)

        resident_data = ResidentDataAggregate(postal_code=postal_code, population=residents_count)

        return resident_data
