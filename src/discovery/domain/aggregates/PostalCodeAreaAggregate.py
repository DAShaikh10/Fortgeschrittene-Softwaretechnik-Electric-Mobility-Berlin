"""
Discovery Domain Aggregate - Postal Code Area Aggregate Module.
"""

from typing import List
from dataclasses import dataclass, field

from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode
from src.shared.domain.aggregates.BaseAggregate import BaseAggregate
from src.shared.domain.events import DomainEvent, StationSearchPerformedEvent


@dataclass
class PostalCodeAreaAggregate(BaseAggregate):
    """
    Aggregate Root: Represents a postal code area with its charging infrastructure.
    """

    postal_code: PostalCode  # Identity
    stations: List[ChargingStation] = field(default_factory=list)
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_station(self, station: ChargingStation):
        """
        Add a charging station to this area

        Args:
            station (ChargingStation): ChargingStation entity to add

        Raises:
            ValueError: If the station is not a ChargingStation entity
        """

        if not isinstance(station, ChargingStation):
            raise ValueError("Must be a ChargingStation entity")

        self.stations.append(station)

    def get_station_count(self) -> int:
        """
        Query: Total number of stations.

        Returns:
            int: Number of stations in this postal code area.
        """
        return len(self.stations)

    # def get_fast_charger_count(self) -> int:
    #     """Query: Count of fast chargers (>=50kW)"""
    #     return sum(1 for station in self.stations if station.is_fast_charger())

    # def get_total_capacity_kw(self) -> float:
    #     """Query: Total charging capacity"""
    #     return sum(station.power_kw for station in self.stations)

    # def get_average_power_kw(self) -> float:
    #     """Query: Average power per station"""
    #     if not self.stations:
    #         return 0.0
    #     return self.get_total_capacity_kw() / len(self.stations)

    # def has_fast_charging(self) -> bool:
    #     """Business rule: Area has fast charging capability"""
    #     return self.get_fast_charger_count() > 0

    # def is_well_equipped(self) -> bool:
    #     """
    #     Business rule: Area is considered well-equipped.
    #     At least 5 stations OR at least 2 fast chargers.
    #     """
    #     return self.get_station_count() >= 5 or self.get_fast_charger_count() >= 2

    # def get_coverage_level(self) -> str:
    #     """
    #     Business logic: Assess infrastructure coverage level.
    #     """
    #     count = self.get_station_count()
    #     fast_count = self.get_fast_charger_count()

    #     if count == 0:
    #         return "NO_COVERAGE"
    #     elif count >= 20 and fast_count >= 5:
    #         return "EXCELLENT"
    #     elif count >= 10 and fast_count >= 2:
    #         return "GOOD"
    #     elif count >= 5:
    #         return "ADEQUATE"
    #     else:
    #         return "POOR"

    # def get_stations_by_category(self) -> dict:
    #     """Group stations by charging category"""
    #     categories = {}
    #     for station in self.stations:
    #         category = station.get_charging_category()
    #         if category not in categories:
    #             categories[category] = []
    #         categories[category].append(station)
    #     return categories

    def perform_search(self, search_parameters: dict = None):
        """
        Business operation: Perform a search and emit domain event.

        Args:
            search_parameters: Optional search filters
        """
        if search_parameters is None:
            search_parameters = {}

        # Emit domain event.
        self._domain_events.append(
            StationSearchPerformedEvent(
                postal_code=self.postal_code,
                stations_found=self.get_station_count(),
                search_parameters=search_parameters,
            )
        )
