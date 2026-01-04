"""
Discovery Domain Aggregate - Postal Code Area Aggregate Module.
"""

from typing import List

from src.shared.domain.entities import ChargingStation
from src.shared.domain.aggregates import BaseAggregate
from src.shared.domain.value_objects import PostalCode
from src.shared.domain.enums import CoverageLevel
from src.shared.domain.events import StationSearchPerformedEvent


class PostalCodeAreaAggregate(BaseAggregate):
    """
    Aggregate Root: Represents a postal code area with its charging infrastructure.

    Responsibilities:
    - Manage charging station entities within this postal code area
    - Enforce business rules about infrastructure coverage
    - Calculate metrics and assessments
    - Generate domain events for search operations

    Business Invariants:
    - Postal code must be valid
    - All stations must be ChargingStation entities
    - Station list must be non-null
    """

    def __init__(self, postal_code: PostalCode, stations: List[ChargingStation] = None):
        """
        Initialize the PostalCodeAreaAggregate.

        Args:
            postal_code: Postal code identifying the area
            stations: List of charging stations (defaults to empty list)
        """
        # Initialize base aggregate event handling.
        super().__init__()

        # Set instance attributes
        self._postal_code = postal_code
        self._stations = stations if stations is not None else []

        # Validate invariants
        for station in self._stations:
            if not isinstance(station, ChargingStation):
                raise ValueError("All items must be ChargingStation entities")

    @property
    def postal_code(self) -> PostalCode:
        """Get the postal code."""
        return self._postal_code

    @property
    def stations(self) -> List[ChargingStation]:
        """Get a copy of the stations list to protect encapsulation."""
        return self._stations.copy()

    @staticmethod
    def create(postal_code: PostalCode) -> "PostalCodeAreaAggregate":
        """
        Factory Method: Create a new postal code area aggregate.

        Args:
            postal_code: PostalCode value object for the area.

        Returns:
            PostalCodeAreaAggregate: Newly created aggregate with empty stations list.
        """
        return PostalCodeAreaAggregate(postal_code=postal_code, stations=[])

    @staticmethod
    def create_with_stations(postal_code: PostalCode, stations: List[ChargingStation]) -> "PostalCodeAreaAggregate":
        """
        Factory Method: Create aggregate with initial stations.

        Args:
            postal_code: PostalCode value object for the area.
            stations: List of ChargingStation entities.

        Returns:
            PostalCodeAreaAggregate: Aggregate with pre-populated stations.

        Raises:
            ValueError: If any item in stations is not a ChargingStation.
        """
        return PostalCodeAreaAggregate(postal_code=postal_code, stations=stations.copy())

    def get_postal_code(self) -> PostalCode:
        """
        Query: Get the postal code for this area.

        Returns:
            PostalCode: Postal code value object.
        """
        return self._postal_code

    def get_stations(self) -> List[ChargingStation]:
        """
        Query: Get all charging stations in this area.

        Returns:
            List[ChargingStation]: Copy of stations list to protect encapsulation.
        """
        return self._stations.copy()

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

        self._stations.append(station)

    def get_station_count(self) -> int:
        """
        Query: Total number of stations.

        Returns:
            int: Number of stations in this postal code area.
        """
        return len(self._stations)

    def get_fast_charger_count(self) -> int:
        """
        Query: Count of fast chargers (>=50kW).

        Returns:
            int: Number of fast charging stations in this area.
        """
        return sum(1 for station in self._stations if station.is_fast_charger())

    def get_total_capacity_kw(self) -> float:
        """
        Query: Total charging capacity across all stations.

        Returns:
            float: Sum of power capacity in kilowatts.
        """
        return sum(station.power_capacity.kilowatts for station in self._stations)

    def get_average_power_kw(self) -> float:
        """
        Query: Average power per station in this area.

        Returns:
            float: Average power in kW, or 0.0 if no stations.
        """
        if not self._stations:
            return 0.0
        return self.get_total_capacity_kw() / len(self._stations)

    def has_fast_charging(self) -> bool:
        """
        Business rule: Check if area has fast charging capability.

        Returns:
            bool: True if at least one fast charger exists.
        """
        return self.get_fast_charger_count() > 0

    def is_well_equipped(self) -> bool:
        """
        Business rule: Determine if area is well-equipped with charging infrastructure.

        Well-equipped is defined as having either:
        - At least 5 stations (quantity), OR
        - At least 2 fast chargers (quality)

        Returns:
            bool: True if area meets well-equipped criteria.
        """
        return self.get_station_count() >= 5 or self.get_fast_charger_count() >= 2

    def get_coverage_level(self) -> CoverageLevel:
        """
        Business logic: Assess infrastructure coverage level for this area.

        Coverage levels:
        - NO_COVERAGE: No stations available
        - POOR: < 5 stations
        - ADEQUATE: 5+ stations
        - GOOD: 10+ stations with 2+ fast chargers
        - EXCELLENT: 20+ stations with 5+ fast chargers

        Returns:
            CoverageLevel: Coverage level assessment.
        """
        count = self.get_station_count()
        fast_count = self.get_fast_charger_count()

        if count == 0:
            return CoverageLevel.NO_COVERAGE

        if count >= 20 and fast_count >= 5:
            return CoverageLevel.EXCELLENT
        if count >= 10 and fast_count >= 2:
            return CoverageLevel.GOOD
        if count >= 5:
            return CoverageLevel.ADEQUATE

        return CoverageLevel.POOR

    def get_stations_by_category(self) -> dict:
        """
        Query: Group stations by their charging speed category.

        Returns:
            dict: Dictionary mapping ChargingSpeed categories to lists of stations.
        """
        categories = {}
        for station in self._stations:
            category = station.get_charging_category()
            if category not in categories:
                categories[category] = []
            categories[category].append(station)
        return categories

    def perform_search(self, search_parameters: dict = None):
        """
        Business operation: Perform a search and emit domain event.

        Args:
            search_parameters: Optional search filters
        """
        if search_parameters is None:
            search_parameters = {}

        # Emit domain event using consistent method.
        event = StationSearchPerformedEvent(
            postal_code=self._postal_code,
            stations_found=self.get_station_count(),
            search_parameters=search_parameters,
        )
        self._add_domain_event(event)
