"""
Shared Application Service for Charging Station operations.
"""

from typing import List

from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.repositories import ChargingStationRepository
from src.discovery.application.dtos import PostalCodeAreaDTO
from src.discovery.domain.aggregates import PostalCodeAreaAggregate

from .base_service import BaseService


class ChargingStationService(BaseService):
    """
    Application Service for charging station operations.
    """

    def __init__(self, repository: ChargingStationRepository, event_bus: IDomainEventPublisher):
        """
        Initialize the ChargingStationService.
        Args:
            repository: Repository for charging stations.
            event_bus: Domain event publisher interface.
        """

        super().__init__(repository, event_bus)

    def search_by_postal_code(self, postal_code: PostalCode) -> PostalCodeAreaDTO:
        """
        Search for charging stations by postal code.

        This is the main use case for station discovery.
        Returns a DTO with all station data and business metrics.

        Args:
            postal_code (PostalCode): Postal code to search for.

        Returns:
            PostalCodeAreaDTO: DTO containing stations and coverage information.

        Raises:
            Exception: Re-raises any exception after emitting failure event.
        """

        aggregate = PostalCodeAreaAggregate(postal_code=postal_code)

        try:
            stations: List[ChargingStation] = self._repository.find_stations_by_postal_code(postal_code)
            for station in stations:
                aggregate.add_station(station)

            # Emit appropriate event based on results
            if len(stations) == 0:
                aggregate.record_no_stations()
            else:
                aggregate.record_stations_found()

            self.publish_events(aggregate)

            return PostalCodeAreaDTO.from_aggregate(aggregate)

        except Exception as e:
            # Emit failure event
            error_type = type(e).__name__
            aggregate.fail_search(error_message=str(e), error_type=error_type)
            self.publish_events(aggregate)

            # Re-raise the exception for the caller to handle
            raise

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
