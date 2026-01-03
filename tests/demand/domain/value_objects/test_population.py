"""
Unit Tests for Population Value Object.

Test categories:
- Validation tests (type and value constraints)
- Conversion tests (__int__, __str__, __repr__)
- Immutability tests
- Edge cases and boundary values
"""

import pytest

from src.demand.domain.value_objects import Population


class TestPopulationValidation:
    """Test validation logic in __post_init__."""

    def test_valid_population_creation(self):
        """Test creating a valid Population instance."""
        population = Population(30000)

        assert population.value == 30000

    def test_zero_population_is_valid(self):
        """Test that zero population is valid."""
        population = Population(0)

        assert population.value == 0

    def test_large_population_is_valid(self):
        """Test with large population value."""
        population = Population(10000000)

        assert population.value == 10000000

    def test_negative_population_raises_value_error(self):
        """Test that negative population raises ValueError."""
        with pytest.raises(ValueError, match="Population cannot be negative"):
            Population(-1)

    def test_negative_large_population_raises_value_error(self):
        """Test that large negative population raises ValueError."""
        with pytest.raises(ValueError, match="Population cannot be negative, got: -50000"):
            Population(-50000)

    def test_float_population_raises_type_error(self):
        """Test that float value raises TypeError."""
        with pytest.raises(TypeError, match="Population must be an integer"):
            Population(1500.5)

    def test_string_population_raises_type_error(self):
        """Test that string value raises TypeError."""
        with pytest.raises(TypeError, match="Population must be an integer"):
            Population("30000")

    def test_none_population_raises_type_error(self):
        """Test that None value raises TypeError."""
        with pytest.raises(TypeError, match="Population must be an integer"):
            Population(None)


class TestPopulationConversion:
    """Test conversion methods."""

    def test_int_conversion(self):
        """Test __int__ conversion method."""
        population = Population(25000)

        assert int(population) == 25000

    def test_int_conversion_with_zero(self):
        """Test __int__ conversion with zero."""
        population = Population(0)

        assert int(population) == 0

    def test_str_conversion(self):
        """Test __str__ conversion method."""
        population = Population(30000)

        assert str(population) == "30000"

    def test_str_conversion_with_zero(self):
        """Test __str__ conversion with zero."""
        population = Population(0)

        assert str(population) == "0"

    def test_repr_representation(self):
        """Test __repr__ method."""
        population = Population(15000)

        assert repr(population) == "Population(15000)"

    def test_repr_with_zero(self):
        """Test __repr__ with zero value."""
        population = Population(0)

        assert repr(population) == "Population(0)"


class TestPopulationEquality:
    """Test equality and comparison."""

    def test_two_populations_with_same_value_are_equal(self):
        """Test that populations with same value are equal."""
        pop1 = Population(30000)
        pop2 = Population(30000)

        assert pop1 == pop2

    def test_two_populations_with_different_values_are_not_equal(self):
        """Test that populations with different values are not equal."""
        pop1 = Population(30000)
        pop2 = Population(25000)

        assert pop1 != pop2

    def test_population_equality_with_zero(self):
        """Test equality with zero values."""
        pop1 = Population(0)
        pop2 = Population(0)

        assert pop1 == pop2


class TestPopulationImmutability:
    """Test immutability of Population (frozen dataclass)."""

    def test_cannot_modify_value(self):
        """Test that value attribute cannot be modified."""
        population = Population(30000)

        with pytest.raises(AttributeError):
            population.value = 50000


class TestPopulationUsageInCalculations:
    """Test Population in mathematical operations."""

    def test_population_in_division(self):
        """Test using population in division calculation."""
        population = Population(30000)
        stations = 5

        result = int(population) / stations

        assert result == 6000.0

    def test_population_in_addition(self):
        """Test using population in addition."""
        pop1 = Population(20000)
        pop2 = Population(15000)

        total = int(pop1) + int(pop2)

        assert total == 35000

    def test_population_in_comparison(self):
        """Test using population in comparison."""
        pop1 = Population(30000)
        pop2 = Population(25000)

        assert int(pop1) > int(pop2)
        assert int(pop2) < int(pop1)


class TestPopulationBoundaryValues:
    """Test boundary values and edge cases."""

    def test_minimum_valid_population(self):
        """Test minimum valid population (zero)."""
        population = Population(0)

        assert population.value == 0
        assert int(population) == 0

    def test_population_one(self):
        """Test population of one."""
        population = Population(1)

        assert population.value == 1

    def test_very_large_population(self):
        """Test with very large population value."""
        population = Population(999999999)

        assert population.value == 999999999
        assert int(population) == 999999999


class TestPopulationIntegration:
    """Integration tests for Population value object."""

    def test_population_workflow(self):
        """Test complete workflow with population."""
        # Create population
        population = Population(30000)

        # Use in calculation
        residents_per_station = int(population) / 5

        # Verify value preservation
        assert population.value == 30000
        assert residents_per_station == 6000.0

        # Verify string conversion
        assert str(population) == "30000"
        assert repr(population) == "Population(30000)"

    def test_multiple_population_objects(self):
        """Test creating multiple population objects."""
        populations = [
            Population(10000),
            Population(25000),
            Population(50000),
        ]

        assert len(populations) == 3
        assert all(isinstance(p, Population) for p in populations)
        assert sum(int(p) for p in populations) == 85000

    def test_population_in_data_structure(self):
        """Test storing populations in collections."""
        population_dict = {
            "area1": Population(30000),
            "area2": Population(25000),
            "area3": Population(15000),
        }

        assert len(population_dict) == 3
        assert int(population_dict["area1"]) == 30000
        assert int(population_dict["area2"]) == 25000
