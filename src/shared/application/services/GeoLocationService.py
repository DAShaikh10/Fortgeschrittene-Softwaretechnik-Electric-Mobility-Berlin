"""
Shared Application Service for Geographic Location Data.
"""

from src.shared.domain.events import DomainEventBus
from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.infrastructure.repositories import GeoDataRepository

from .BaseService import BaseService


class GeoLocationService(BaseService):
    """
    Application service for geographic location data.
    """

    def __init__(self, repository: GeoDataRepository, event_bus: DomainEventBus):
        """
        Initialize the GeoLocationService.

        Args:
            repository (GeoDataRepository): Repository for geographic data.
            event_bus (DomainEventBus): Domain event bus.
        """

        super().__init__(repository, event_bus)

    def get_geolocation_data_for_postal_code(self, postal_code: PostalCode) -> GeoLocation:
        """
        Fetch geographic data for a given postal code.

        Args:
            postal_code (PostalCode): The postal code to fetch geographic data for.

        Returns:
            GeoLocation: Geographic location data for the given postal code or None if not found.
        """

        return self._repository.fetch_geolocation_data(postal_code)

    def get_all_plzs(self) -> list[int]:
        """
        Retrieve all valid postal codes available in the geographic dataset.

        Returns:
            list[int]: A list of valid postal code integers.
        """
        return self._repository.get_all_postal_codes()
