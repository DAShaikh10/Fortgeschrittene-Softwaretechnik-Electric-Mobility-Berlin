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

        super().__init__(repository, event_bus)

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

        aggregate = PostalCodeAreaAggregate(postal_code=postal_code)

        stations: List[ChargingStation] = self._repository.find_stations_by_postal_code(postal_code)
        for station in stations:
            aggregate.add_station(station)

        aggregate.perform_search(search_parameters={"postal_code": postal_code.value})

        self._publish_events(aggregate)

        return aggregate

    def find_stations_by_postal_code(self, postal_code: PostalCode) -> List[ChargingStation]:
        """
        Retrieve all charging stations located within a specific postal code area.

        This method provides a simple query interface for retrieving station entities
        without the full aggregate context. Useful for lightweight data access scenarios.

        Args:
            postal_code (PostalCode): The postal code value object to query.

        Returns:
            List[ChargingStation]: Collection of charging station entities in the area.
                                   Returns empty list if no stations found.
        """
        return self._repository.find_stations_by_postal_code(postal_code)
