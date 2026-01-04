"""
Domain Service for Capacity Classification.

This service encapsulates business logic for classifying power capacities
into categories (Low, Medium, High, None) based on quantile analysis.
"""

from typing import Dict, List, Tuple


class CapacityClassificationService:
    """
    Domain Service: Classifies power capacities into categories.

    This service contains business logic that doesn't naturally belong
    to a single aggregate or value object. It implements the capacity
    classification rules based on quantile analysis.

    Business Rules:
    - Capacities are classified using 33rd and 66th percentiles
    - Zero capacity is always classified as "None"
    - Classification is based on non-zero capacities only
    """

    @staticmethod
    def calculate_quantiles(capacities: List[float]) -> Tuple[float, float]:
        """
        Calculate the 33rd and 66th percentiles for capacity classification.

        Args:
            capacities: List of capacity values (should be non-zero)

        Returns:
            Tuple of (q33, q66) representing the 33rd and 66th percentiles

        Raises:
            ValueError: If capacities list is empty
        """
        if not capacities:
            raise ValueError("Cannot calculate quantiles from empty list")

        sorted_capacities = sorted(capacities)
        q33_index = int(len(sorted_capacities) * 0.33)
        q66_index = int(len(sorted_capacities) * 0.66)

        q33 = sorted_capacities[q33_index] if q33_index < len(sorted_capacities) else sorted_capacities[-1]
        q66 = sorted_capacities[q66_index] if q66_index < len(sorted_capacities) else sorted_capacities[-1]

        return q33, q66

    @staticmethod
    def classify_capacity(capacity: float, q33: float, q66: float) -> str:
        """
        Classify a single capacity value into a category.

        Args:
            capacity: The capacity value to classify
            q33: 33rd percentile threshold
            q66: 66th percentile threshold

        Returns:
            Category string: "None", "Low", "Medium", or "High"
        """
        if capacity == 0:
            return "None"
        if capacity <= q33:
            return "Low"
        if capacity <= q66:
            return "Medium"
        return "High"

    @staticmethod
    def classify_capacities(capacities: List[float]) -> Tuple[Dict[str, Tuple[float, float]], List[str]]:
        """
        Classify a list of capacities and return range definitions and categories.

        Args:
            capacities: List of capacity values to classify

        Returns:
            Tuple of:
            - range_definitions: Dict mapping category to (min, max) capacity range
            - categories: List of category strings corresponding to input capacities
        """
        if not capacities:
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, []

        max_capacity = max(capacities) if capacities else 0.0

        if max_capacity == 0:
            # All capacities are zero
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, ["None"] * len(capacities)

        # Filter out zero capacity areas for classification
        non_zero_capacities = [cap for cap in capacities if cap > 0]

        if len(non_zero_capacities) == 0:
            # All capacities are zero
            return {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}, ["None"] * len(capacities)

        # Calculate quantiles from non-zero capacities
        q33, q66 = CapacityClassificationService.calculate_quantiles(non_zero_capacities)

        # Define ranges
        range_definitions = {"Low": (0, q33), "Medium": (q33, q66), "High": (q66, max_capacity)}

        # Classify each capacity
        categories = [CapacityClassificationService.classify_capacity(capacity, q33, q66) for capacity in capacities]

        return range_definitions, categories
