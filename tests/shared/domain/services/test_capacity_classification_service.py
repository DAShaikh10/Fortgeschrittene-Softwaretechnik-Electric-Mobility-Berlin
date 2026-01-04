"""
Unit Tests for CapacityClassificationService.

Test categories:
- Quantile calculation tests
- Capacity classification tests
- Range definition tests
- Edge cases and validation
"""

# pylint: disable=redefined-outer-name

import pytest

from src.shared.domain.enums import CapacityCategory
from src.shared.domain.services import CapacityClassificationService


class TestCalculateQuantiles:
    """Test calculate_quantiles method."""

    def test_calculates_quantiles_correctly(self):
        """Test that method calculates 33rd and 66th percentiles correctly."""
        capacities = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

        q33, q66 = CapacityClassificationService.calculate_quantiles(capacities)

        # With 10 values, q33 should be around index 3 (30.0) and q66 around index 6 (70.0)
        assert isinstance(q33, float)
        assert isinstance(q66, float)
        assert q33 <= q66
        assert q33 >= min(capacities)
        assert q66 <= max(capacities)

    def test_handles_small_lists(self):
        """Test that method handles small capacity lists."""
        capacities = [10.0, 50.0, 100.0]

        q33, q66 = CapacityClassificationService.calculate_quantiles(capacities)

        assert q33 <= q66
        assert q33 in capacities
        assert q66 in capacities

    def test_raises_error_for_empty_list(self):
        """Test that method raises ValueError for empty list."""
        with pytest.raises(ValueError, match="Cannot calculate quantiles from empty list"):
            CapacityClassificationService.calculate_quantiles([])

    def test_handles_single_value(self):
        """Test that method handles single value list."""
        capacities = [50.0]

        q33, q66 = CapacityClassificationService.calculate_quantiles(capacities)

        assert q33 == 50.0
        assert q66 == 50.0


class TestClassifyCapacity:
    """Test classify_capacity method."""

    def test_classifies_zero_as_none(self):
        """Test that zero capacity is classified as 'None'."""
        category = CapacityClassificationService.classify_capacity(0.0, 50.0, 100.0)

        assert category == CapacityCategory.NONE

    def test_classifies_low_capacity(self):
        """Test that capacity <= q33 is classified as 'Low'."""
        q33 = 50.0
        q66 = 100.0

        category = CapacityClassificationService.classify_capacity(30.0, q33, q66)

        assert category == CapacityCategory.LOW

    def test_classifies_medium_capacity(self):
        """Test that capacity between q33 and q66 is classified as 'Medium'."""
        q33 = 50.0
        q66 = 100.0

        category = CapacityClassificationService.classify_capacity(75.0, q33, q66)

        assert category == CapacityCategory.MEDIUM

    def test_classifies_high_capacity(self):
        """Test that capacity > q66 is classified as 'High'."""
        q33 = 50.0
        q66 = 100.0

        category = CapacityClassificationService.classify_capacity(150.0, q33, q66)

        assert category == CapacityCategory.HIGH

    def test_classifies_at_boundaries(self):
        """Test classification at exact quantile boundaries."""
        q33 = 50.0
        q66 = 100.0

        assert CapacityClassificationService.classify_capacity(50.0, q33, q66) == CapacityCategory.LOW
        assert CapacityClassificationService.classify_capacity(100.0, q33, q66) == CapacityCategory.MEDIUM
        assert CapacityClassificationService.classify_capacity(100.1, q33, q66) == CapacityCategory.HIGH


class TestClassifyCapacities:
    """Test classify_capacities method."""

    def test_classifies_multiple_capacities(self):
        """Test that method classifies multiple capacities correctly."""
        capacities = [10.0, 50.0, 100.0, 200.0, 300.0]

        range_definitions, categories = CapacityClassificationService.classify_capacities(capacities)

        # Check range definitions structure
        assert "Low" in range_definitions
        assert "Medium" in range_definitions
        assert "High" in range_definitions
        assert len(categories) == 5
        assert all(cat in [CapacityCategory.LOW, CapacityCategory.MEDIUM, CapacityCategory.HIGH] for cat in categories)

    def test_handles_empty_list(self):
        """Test that method handles empty list."""
        range_definitions, categories = CapacityClassificationService.classify_capacities([])

        assert range_definitions == {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}
        assert categories == []

    def test_handles_all_zero_capacities(self):
        """Test that method handles all zero capacities."""
        capacities = [0.0, 0.0, 0.0]

        range_definitions, categories = CapacityClassificationService.classify_capacities(capacities)

        assert range_definitions == {"Low": (0, 0), "Medium": (0, 0), "High": (0, 0)}
        assert categories == ["None", "None", "None"]

    def test_handles_mixed_zero_and_nonzero(self):
        """Test that method handles mix of zero and non-zero capacities."""
        capacities = [0.0, 50.0, 100.0]

        range_definitions, categories = CapacityClassificationService.classify_capacities(capacities)

        assert categories[0] == CapacityCategory.NONE
        assert categories[1] in [CapacityCategory.LOW, CapacityCategory.MEDIUM, CapacityCategory.HIGH]
        assert categories[2] in [CapacityCategory.LOW, CapacityCategory.MEDIUM, CapacityCategory.HIGH]
        assert "Low" in range_definitions
        assert "Medium" in range_definitions
        assert "High" in range_definitions

    def test_range_definitions_are_valid(self):
        """Test that range definitions have valid min/max values."""
        capacities = [10.0, 50.0, 100.0, 200.0]

        range_definitions, _ = CapacityClassificationService.classify_capacities(capacities)

        for _, (min_val, max_val) in range_definitions.items():
            assert isinstance(min_val, (int, float))
            assert isinstance(max_val, (int, float))
            assert min_val <= max_val

    def test_categories_match_capacities_length(self):
        """Test that categories list matches input capacities length."""
        capacities = [10.0, 20.0, 30.0, 40.0, 50.0]

        _, categories = CapacityClassificationService.classify_capacities(capacities)

        assert len(categories) == len(capacities)
