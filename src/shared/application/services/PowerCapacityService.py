"""
Shared Application Service for Power Capacity Analysis.
"""

from typing import Dict, List, Tuple

from src.shared.application.dtos import PowerCapacityDTO
from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.repositories import ChargingStationRepository


class PowerCapacityService:
    """
    Application service for analyzing power capacity by postal code.
    """

    def __init__(self, charging_station_repository: ChargingStationRepository):
        """
        Initialize PowerCapacityService.

        Args:
            charging_station_repository: Repository for accessing charging station data.
        """
        self._repository = charging_station_repository

    def get_power_capacity_by_postal_code(self, postal_codes: List[PostalCode]) -> List[PowerCapacityDTO]:
        """
        Calculate total power capacity (in kW) for each postal code.

        Args:
            postal_codes: List of postal codes to analyze.

        Returns:
            List of PowerCapacityDTO objects with postal_code, total_capacity_kw, and station_count.
        """
        capacity_data = []

        for postal_code in postal_codes:
            stations = self._repository.find_stations_by_postal_code(postal_code)

            if stations:
                total_capacity = sum(station.power_capacity.kilowatts for station in stations)
                capacity_data.append(
                    PowerCapacityDTO(
                        postal_code=postal_code.value,
                        total_capacity_kw=total_capacity,
                        station_count=len(stations),
                    )
                )
            else:
                capacity_data.append(
                    PowerCapacityDTO(
                        postal_code=postal_code.value,
                        total_capacity_kw=0.0,
                        station_count=0,
                    )
                )

        return capacity_data

    def classify_capacity_ranges(
        self, capacity_dtos: List[PowerCapacityDTO]
    ) -> Tuple[Dict[str, Tuple[float, float]], List[PowerCapacityDTO]]:
        """
        Classify postal codes into Low, Medium, and High capacity ranges using quantiles.

        Args:
            capacity_dtos: List of PowerCapacityDTO objects with postal code capacity data.

        Returns:
            Tuple of (range_definitions, capacity_dtos_with_category)
            - range_definitions: Dict mapping category to (min, max) capacity
            - capacity_dtos_with_category: List of PowerCapacityDTO with capacity_category set
        """
        if not capacity_dtos:
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, capacity_dtos

        # Get all capacities and find max
        capacities = [dto.total_capacity_kw for dto in capacity_dtos]
        max_capacity = max(capacities) if capacities else 0.0

        if max_capacity == 0:
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, capacity_dtos

        # Filter out zero capacity areas for classification
        non_zero_capacities = [cap for cap in capacities if cap > 0]

        if len(non_zero_capacities) == 0:
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, capacity_dtos

        # Calculate quantiles (33rd and 66th percentiles)
        sorted_capacities = sorted(non_zero_capacities)
        q33_index = int(len(sorted_capacities) * 0.33)
        q66_index = int(len(sorted_capacities) * 0.66)
        q33 = sorted_capacities[q33_index] if q33_index < len(sorted_capacities) else sorted_capacities[-1]
        q66 = sorted_capacities[q66_index] if q66_index < len(sorted_capacities) else sorted_capacities[-1]

        # Define ranges
        range_definitions = {"Low": (0, q33), "Medium": (q33, q66), "High": (q66, max_capacity)}

        # Classify each postal code and create new DTOs with category
        def classify_capacity(capacity: float) -> str:
            if capacity == 0:
                return "None"
            if capacity <= q33:
                return "Low"
            if capacity <= q66:
                return "Medium"
            return "High"

        capacity_dtos_with_category = [
            PowerCapacityDTO(
                postal_code=dto.postal_code,
                total_capacity_kw=dto.total_capacity_kw,
                station_count=dto.station_count,
                capacity_category=classify_capacity(dto.total_capacity_kw),
            )
            for dto in capacity_dtos
        ]

        return range_definitions, capacity_dtos_with_category

    def get_color_for_capacity(self, capacity: float, max_capacity: float) -> str:
        """
        Generate a color from light to dark blue based on capacity.
        Higher capacity = darker blue.

        Args:
            capacity: The capacity value to colorize.
            max_capacity: The maximum capacity for normalization.

        Returns:
            Hex color code.
        """
        if max_capacity == 0 or capacity == 0:
            return "#f0f0f0"  # Light gray for no capacity

        # Normalize capacity to 0-1 range
        normalized = min(capacity / max_capacity, 1.0)

        # Color gradient from light blue to dark blue
        # Light: #e3f2fd (RGB: 227, 242, 253)
        # Dark: #0d47a1 (RGB: 13, 71, 161)

        r = int(227 - (227 - 13) * normalized)
        g = int(242 - (242 - 71) * normalized)
        b = int(253 - (253 - 161) * normalized)

        return f"#{r:02x}{g:02x}{b:02x}"

    def filter_by_capacity_category(self, capacity_dtos: List[PowerCapacityDTO], category: str) -> List[PowerCapacityDTO]:
        """
        Filter postal codes by capacity category.

        Args:
            capacity_dtos: List of PowerCapacityDTO objects with capacity_category set.
            category: Category to filter by ('Low', 'Medium', 'High', 'All').

        Returns:
            Filtered list of PowerCapacityDTO objects.
        """
        if category == "All":
            return capacity_dtos

        return [dto for dto in capacity_dtos if dto.capacity_category == category]
