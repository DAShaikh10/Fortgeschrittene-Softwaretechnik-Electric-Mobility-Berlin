"""
Unit Tests for StationCount Value Object.

Test categories:
- Validation tests (type and value constraints)
- Conversion tests (__int__, __str__, __repr__)
- Business logic tests (is_zero)
- Immutability tests
- Edge cases and boundary values
"""

import pytest

from src.demand.domain.value_objects import StationCount, Population, DemandPriority


class TestStationCountValidation:
    """Test validation logic in __post_init__."""

    def test_valid_station_count_creation(self):
        """Test creating a valid StationCount instance."""
        station_count = StationCount(10)

        assert station_count.value == 10

    def test_zero_station_count_is_valid(self):
        """Test that zero station count is valid."""
        station_count = StationCount(0)

        assert station_count.value == 0

    def test_large_station_count_is_valid(self):
        """Test with large station count value."""
        station_count = StationCount(10000)

        assert station_count.value == 10000

    def test_negative_station_count_raises_value_error(self):
        """Test that negative station count raises ValueError."""
        with pytest.raises(ValueError, match="Station count cannot be negative"):
            StationCount(-1)

    def test_negative_large_station_count_raises_value_error(self):
        """Test that large negative station count raises ValueError."""
        with pytest.raises(ValueError, match="Station count cannot be negative, got: -100"):
            StationCount(-100)

    def test_float_station_count_raises_type_error(self):
        """Test that float value raises TypeError."""
        with pytest.raises(TypeError, match="Station count must be an integer"):
            StationCount(5.5)

    def test_string_station_count_raises_type_error(self):
        """Test that string value raises TypeError."""
        with pytest.raises(TypeError, match="Station count must be an integer"):
            StationCount("10")

    def test_none_station_count_raises_type_error(self):
        """Test that None value raises TypeError."""
        with pytest.raises(TypeError, match="Station count must be an integer"):
            StationCount(None)


class TestStationCountConversion:
    """Test conversion methods."""

    def test_int_conversion(self):
        """Test __int__ conversion method."""
        station_count = StationCount(15)

        assert int(station_count) == 15

    def test_int_conversion_with_zero(self):
        """Test __int__ conversion with zero."""
        station_count = StationCount(0)

        assert int(station_count) == 0

    def test_str_conversion(self):
        """Test __str__ conversion method."""
        station_count = StationCount(20)

        assert str(station_count) == "20"

    def test_str_conversion_with_zero(self):
        """Test __str__ conversion with zero."""
        station_count = StationCount(0)

        assert str(station_count) == "0"

    def test_repr_representation(self):
        """Test __repr__ method."""
        station_count = StationCount(8)

        assert repr(station_count) == "StationCount(8)"

    def test_repr_with_zero(self):
        """Test __repr__ with zero value."""
        station_count = StationCount(0)

        assert repr(station_count) == "StationCount(0)"


class TestStationCountBusinessLogic:
    """Test business logic methods."""

    def test_is_zero_returns_true_for_zero_stations(self):
        """Test is_zero returns True when no stations exist."""
        station_count = StationCount(0)

        assert station_count.is_zero() is True

    def test_is_zero_returns_false_for_one_station(self):
        """Test is_zero returns False for one station."""
        station_count = StationCount(1)

        assert station_count.is_zero() is False

    def test_is_zero_returns_false_for_multiple_stations(self):
        """Test is_zero returns False for multiple stations."""
        station_count = StationCount(10)

        assert station_count.is_zero() is False

    def test_is_zero_critical_shortage_indicator(self):
        """Test is_zero as critical shortage indicator."""
        station_count = StationCount(0)

        # Zero stations indicates critical infrastructure shortage
        assert station_count.is_zero() is True
        assert station_count.value == 0


class TestStationCountEquality:
    """Test equality and comparison."""

    def test_two_station_counts_with_same_value_are_equal(self):
        """Test that station counts with same value are equal."""
        count1 = StationCount(5)
        count2 = StationCount(5)

        assert count1 == count2

    def test_two_station_counts_with_different_values_are_not_equal(self):
        """Test that station counts with different values are not equal."""
        count1 = StationCount(5)
        count2 = StationCount(10)

        assert count1 != count2

    def test_station_count_equality_with_zero(self):
        """Test equality with zero values."""
        count1 = StationCount(0)
        count2 = StationCount(0)

        assert count1 == count2


class TestStationCountImmutability:
    """Test immutability of StationCount (frozen dataclass)."""

    def test_cannot_modify_value(self):
        """Test that value attribute cannot be modified."""
        station_count = StationCount(10)

        with pytest.raises(AttributeError):
            station_count.value = 20


class TestStationCountUsageInCalculations:
    """Test StationCount in mathematical operations."""

    def test_station_count_in_division(self):
        """Test using station count in division calculation."""
        population = 30000
        station_count = StationCount(5)

        result = population / int(station_count)

        assert result == 6000.0

    def test_station_count_in_multiplication(self):
        """Test using station count in multiplication."""
        capacity_per_station = 100
        station_count = StationCount(8)

        total_capacity = capacity_per_station * int(station_count)

        assert total_capacity == 800

    def test_station_count_in_comparison(self):
        """Test using station count in comparison."""
        count1 = StationCount(10)
        count2 = StationCount(5)

        assert int(count1) > int(count2)
        assert int(count2) < int(count1)

    def test_station_count_zero_in_division_handling(self):
        """Test handling division by zero stations."""
        population = 30000
        station_count = StationCount(0)

        # Should handle zero stations appropriately in business logic
        if station_count.is_zero():
            # Critical shortage - population becomes the ratio
            result = float(population)
        else:
            result = population / int(station_count)

        assert result == 30000.0


class TestStationCountBoundaryValues:
    """Test boundary values and edge cases."""

    def test_minimum_valid_station_count(self):
        """Test minimum valid station count (zero)."""
        station_count = StationCount(0)

        assert station_count.value == 0
        assert int(station_count) == 0
        assert station_count.is_zero() is True

    def test_station_count_one(self):
        """Test station count of one."""
        station_count = StationCount(1)

        assert station_count.value == 1
        assert station_count.is_zero() is False

    def test_very_large_station_count(self):
        """Test with very large station count value."""
        station_count = StationCount(999999)

        assert station_count.value == 999999
        assert int(station_count) == 999999
        assert station_count.is_zero() is False


class TestStationCountIntegration:
    """Integration tests for StationCount value object."""

    def test_station_count_workflow(self):
        """Test complete workflow with station count."""
        # Create station count
        station_count = StationCount(5)

        # Use in calculation
        population = 30000
        residents_per_station = population / int(station_count)

        # Verify value preservation
        assert station_count.value == 5
        assert residents_per_station == 6000.0

        # Verify business logic
        assert station_count.is_zero() is False

        # Verify string conversion
        assert str(station_count) == "5"
        assert repr(station_count) == "StationCount(5)"

    def test_station_count_zero_workflow(self):
        """Test workflow with zero stations (critical shortage)."""
        # Create zero station count
        station_count = StationCount(0)

        # Check critical shortage indicator
        assert station_count.is_zero() is True
        assert station_count.value == 0

        # Handle appropriately in business logic
        population = 30000
        if station_count.is_zero():
            # Critical shortage scenario
            residents_per_station = float(population)
        else:
            residents_per_station = population / int(station_count)

        assert residents_per_station == 30000.0

    def test_multiple_station_count_objects(self):
        """Test creating multiple station count objects."""
        station_counts = [
            StationCount(5),
            StationCount(10),
            StationCount(3),
        ]

        assert len(station_counts) == 3
        assert all(isinstance(sc, StationCount) for sc in station_counts)
        assert sum(int(sc) for sc in station_counts) == 18

    def test_station_count_in_data_structure(self):
        """Test storing station counts in collections."""
        station_count_dict = {
            "area1": StationCount(5),
            "area2": StationCount(10),
            "area3": StationCount(0),
        }

        assert len(station_count_dict) == 3
        assert int(station_count_dict["area1"]) == 5
        assert station_count_dict["area3"].is_zero() is True

    def test_station_count_with_demand_priority_calculation(self):
        """Test station count in demand priority context."""
        population = Population(30000)
        station_count = StationCount(5)

        # Calculate priority using both value objects
        priority = DemandPriority.calculate_priority(
            population=population,
            station_count=station_count
        )

        assert priority.residents_per_station == 6000.0
        assert not station_count.is_zero()
