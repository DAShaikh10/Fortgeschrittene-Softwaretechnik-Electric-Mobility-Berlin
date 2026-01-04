"""
Shared Application Service for Power Capacity Analysis.
"""

from typing import Dict, List, Tuple
import pandas as pd

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

    def get_power_capacity_by_postal_code(self, postal_codes: List[PostalCode]) -> pd.DataFrame:
        """
        Calculate total power capacity (in kW) for each postal code.

        Args:
            postal_codes: List of postal codes to analyze.

        Returns:
            DataFrame with columns: postal_code, total_capacity_kw, station_count
        """
        capacity_data = []

        for postal_code in postal_codes:
            stations = self._repository.find_stations_by_postal_code(postal_code)

            if stations:
                total_capacity = sum(station.power_capacity.kilowatts for station in stations)
                capacity_data.append(
                    {
                        "postal_code": postal_code.value,
                        "total_capacity_kw": total_capacity,
                        "station_count": len(stations),
                    }
                )
            else:
                capacity_data.append({"postal_code": postal_code.value, "total_capacity_kw": 0.0, "station_count": 0})

        return pd.DataFrame(capacity_data)

    def classify_capacity_ranges(
        self, capacity_df: pd.DataFrame
    ) -> Tuple[Dict[str, Tuple[float, float]], pd.DataFrame]:
        """
        Classify postal codes into Low, Medium, and High capacity ranges using quantiles.

        Args:
            capacity_df: DataFrame with postal code capacity data.

        Returns:
            Tuple of (range_definitions, capacity_df_with_category)
            - range_definitions: Dict mapping category to (min, max) capacity
            - capacity_df_with_category: Original DataFrame with added 'capacity_category' column
        """
        if capacity_df.empty or capacity_df["total_capacity_kw"].max() == 0:
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, capacity_df

        # Filter out zero capacity areas for classification
        non_zero_capacity = capacity_df[capacity_df["total_capacity_kw"] > 0]["total_capacity_kw"]

        if len(non_zero_capacity) == 0:
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, capacity_df

        # Calculate quantiles (33rd and 66th percentiles)
        q33 = non_zero_capacity.quantile(0.33)
        q66 = non_zero_capacity.quantile(0.66)
        max_capacity = capacity_df["total_capacity_kw"].max()

        # Define ranges
        range_definitions = {"Low": (0, q33), "Medium": (q33, q66), "High": (q66, max_capacity)}

        # Classify each postal code
        def classify_capacity(capacity):
            if capacity == 0:
                return "None"
            if capacity <= q33:
                return "Low"
            if capacity <= q66:
                return "Medium"
            return "High"

        capacity_df = capacity_df.copy()
        capacity_df["capacity_category"] = capacity_df["total_capacity_kw"].apply(classify_capacity)

        return range_definitions, capacity_df

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

    def filter_by_capacity_category(self, capacity_df: pd.DataFrame, category: str) -> pd.DataFrame:
        """
        Filter postal codes by capacity category.

        Args:
            capacity_df: DataFrame with capacity data and 'capacity_category' column.
            category: Category to filter by ('Low', 'Medium', 'High', 'All').

        Returns:
            Filtered DataFrame.
        """
        if category == "All":
            return capacity_df

        return capacity_df[capacity_df["capacity_category"] == category]
