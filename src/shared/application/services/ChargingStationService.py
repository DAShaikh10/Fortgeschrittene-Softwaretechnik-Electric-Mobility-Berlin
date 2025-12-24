"""
Shared Application Service for Charging Station operations.
"""

from typing import List

from src.shared.domain.events import DomainEventBus
from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.repositories import ChargingStationRepository
from src.discovery.domain.aggregates import PostalCodeAreaAggregate

from .BaseService import BaseService


class ChargingStationService(BaseService):
    """
    Application Service for charging station operations.
    """

    def __init__(self, repository: ChargingStationRepository, event_bus: DomainEventBus):
        """
        Initialize the ChargingStationService.
        Args:
            repository: Repository for charging stations.
            event_bus: Domain event bus.
        """

        super().__init__(repository)

        self._event_bus = event_bus

    def search_by_postal_code(self, postal_code: PostalCode) -> PostalCodeAreaAggregate:
        """
        Search for charging stations by postal code.

        This is the main use case for station discovery.
        Returns a `PostalCodeAreaAggregate` with all stations and business logic.

        Args:
            postal_code (PostalCode): Postal code to search for.

        Returns:
            PostalCodeAreaAggregate: Aggregate containing stations and coverage information.
        """

        area = PostalCodeAreaAggregate(postal_code=postal_code)

        stations: List[ChargingStation] = self.repository.find_stations_by_postal_code(postal_code)
        for station in stations:
            area.add_station(station)

        area.perform_search(search_parameters={"postal_code": postal_code.value})

        for event in area.get_domain_events():
            self._event_bus.publish(event)

        area.clear_events()

        return area

    def get_stations_for_all_postal_codes(self) -> List[PostalCodeAreaAggregate]:
        """
        Get All Stations for All Postal Codes.

        Returns:
            List of PostalCodeAreaAggregate with stations for all postal codes.
        """

        self.repository.get_stations_for_all_postal_codes()
