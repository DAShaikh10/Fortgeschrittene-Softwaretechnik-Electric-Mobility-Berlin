"""
Unit Tests for PowerCapacity Value Object.

Test categories:
- Validation tests (invariants)
- Business rules (fast charging threshold)
- Immutability tests
- Edge cases and boundary values
"""

# pylint: disable=redefined-outer-name  # pytest fixtures redefine names

import pytest

from src.shared.domain.value_objects import PowerCapacity


class TestPowerCapacityValidation:
    """Test validation logic in __post_init__."""

    def test_valid_power_capacity_zero(self):
        """Test creating a power capacity with 0 kW (edge case)."""
        power_capacity = PowerCapacity(kilowatts=0.0)

        assert power_capacity.kilowatts == 0.0

    def test_valid_power_capacity_normal_charging(self):
        """Test creating a valid power capacity for normal charging (22 kW)."""
        power_capacity = PowerCapacity(kilowatts=22.0)

        assert power_capacity.kilowatts == 22.0

    def test_valid_power_capacity_fast_charging_threshold(self):
        """Test creating a power capacity at fast charging threshold (50 kW)."""
        power_capacity = PowerCapacity(kilowatts=50.0)

        assert power_capacity.kilowatts == 50.0

    def test_valid_power_capacity_fast_charging(self):
        """Test creating a valid power capacity for fast charging (150 kW)."""
        power_capacity = PowerCapacity(kilowatts=150.0)

        assert power_capacity.kilowatts == 150.0

    def test_valid_power_capacity_ultra_fast_charging(self):
        """Test creating a valid power capacity for ultra-fast charging (350 kW)."""
        power_capacity = PowerCapacity(kilowatts=350.0)

        assert power_capacity.kilowatts == 350.0

    def test_valid_power_capacity_maximum_allowed(self):
        """Test creating a power capacity at maximum allowed value (1000 kW)."""
        power_capacity = PowerCapacity(kilowatts=1000.0)

        assert power_capacity.kilowatts == 1000.0

    def test_negative_power_capacity_raises_error(self):
        """Test that negative power capacity raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity cannot be negative"):
            PowerCapacity(kilowatts=-1.0)

    def test_large_negative_power_capacity_raises_error(self):
        """Test that large negative power capacity raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity cannot be negative"):
            PowerCapacity(kilowatts=-100.0)

    def test_power_capacity_exceeds_maximum_raises_error(self):
        """Test that power capacity exceeding 1000 kW raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity exceeds maximum reasonable value"):
            PowerCapacity(kilowatts=1001.0)

    def test_large_power_capacity_exceeds_maximum_raises_error(self):
        """Test that very large power capacity raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity exceeds maximum reasonable value"):
            PowerCapacity(kilowatts=5000.0)

    def test_fractional_power_capacity(self):
        """Test creating a power capacity with fractional value."""
        power_capacity = PowerCapacity(kilowatts=22.5)

        assert power_capacity.kilowatts == 22.5

    def test_very_small_positive_power_capacity(self):
        """Test creating a very small positive power capacity."""
        power_capacity = PowerCapacity(kilowatts=0.001)

        assert power_capacity.kilowatts == 0.001


class TestPowerCapacityBusinessRules:
    """Test business rules related to fast charging."""

    def test_is_fast_charging_returns_false_for_zero_kw(self):
        """Test that 0 kW is not considered fast charging."""
        power_capacity = PowerCapacity(kilowatts=0.0)

        assert power_capacity.is_fast_charging() is False

    def test_is_fast_charging_returns_false_for_normal_charging(self):
        """Test that normal charging (22 kW) is not fast charging."""
        power_capacity = PowerCapacity(kilowatts=22.0)

        assert power_capacity.is_fast_charging() is False

    def test_is_fast_charging_returns_false_just_below_threshold(self):
        """Test that power just below 50 kW is not fast charging."""
        power_capacity = PowerCapacity(kilowatts=49.9)

        assert power_capacity.is_fast_charging() is False

    def test_is_fast_charging_returns_true_at_threshold(self):
        """Test that exactly 50 kW is considered fast charging."""
        power_capacity = PowerCapacity(kilowatts=50.0)

        assert power_capacity.is_fast_charging() is True

    def test_is_fast_charging_returns_true_just_above_threshold(self):
        """Test that power just above 50 kW is fast charging."""
        power_capacity = PowerCapacity(kilowatts=50.1)

        assert power_capacity.is_fast_charging() is True

    def test_is_fast_charging_returns_true_for_fast_charging(self):
        """Test that fast charging (150 kW) is correctly identified."""
        power_capacity = PowerCapacity(kilowatts=150.0)

        assert power_capacity.is_fast_charging() is True

    def test_is_fast_charging_returns_true_for_ultra_fast_charging(self):
        """Test that ultra-fast charging (350 kW) is correctly identified."""
        power_capacity = PowerCapacity(kilowatts=350.0)

        assert power_capacity.is_fast_charging() is True

    def test_is_fast_charging_returns_true_for_maximum_power(self):
        """Test that maximum power (1000 kW) is fast charging."""
        power_capacity = PowerCapacity(kilowatts=1000.0)

        assert power_capacity.is_fast_charging() is True


class TestPowerCapacityImmutability:
    """Test that PowerCapacity is immutable (frozen dataclass)."""

    def test_cannot_modify_kilowatts_attribute(self):
        """Test that kilowatts attribute cannot be modified after creation."""
        power_capacity = PowerCapacity(kilowatts=50.0)

        with pytest.raises(AttributeError):
            power_capacity.kilowatts = 100.0

    def test_cannot_add_new_attributes(self):
        """Test that new attributes cannot be added to the value object."""
        power_capacity = PowerCapacity(kilowatts=50.0)

        with pytest.raises(AttributeError):
            power_capacity.new_attribute = "value"

    def test_cannot_delete_attributes(self):
        """Test that attributes cannot be deleted from the value object."""
        power_capacity = PowerCapacity(kilowatts=50.0)

        with pytest.raises(AttributeError):
            del power_capacity.kilowatts


class TestPowerCapacityEquality:
    """Test equality and hashing behavior of PowerCapacity."""

    def test_same_power_capacity_values_are_equal(self):
        """Test that two PowerCapacity instances with same value are equal."""
        power_capacity1 = PowerCapacity(kilowatts=50.0)
        power_capacity2 = PowerCapacity(kilowatts=50.0)

        assert power_capacity1 == power_capacity2

    def test_different_power_capacity_values_are_not_equal(self):
        """Test that two PowerCapacity instances with different values are not equal."""
        power_capacity1 = PowerCapacity(kilowatts=50.0)
        power_capacity2 = PowerCapacity(kilowatts=100.0)

        assert power_capacity1 != power_capacity2

    def test_power_capacity_is_hashable(self):
        """Test that PowerCapacity instances can be used as dictionary keys."""
        power_capacity1 = PowerCapacity(kilowatts=50.0)
        power_capacity2 = PowerCapacity(kilowatts=50.0)
        power_capacity3 = PowerCapacity(kilowatts=100.0)

        capacity_dict = {power_capacity1: "fast", power_capacity3: "ultra"}

        assert capacity_dict[power_capacity2] == "fast"
        assert len(capacity_dict) == 2

    def test_power_capacity_can_be_used_in_set(self):
        """Test that PowerCapacity instances can be added to sets."""
        power_capacity1 = PowerCapacity(kilowatts=50.0)
        power_capacity2 = PowerCapacity(kilowatts=50.0)
        power_capacity3 = PowerCapacity(kilowatts=100.0)

        capacity_set = {power_capacity1, power_capacity2, power_capacity3}

        assert len(capacity_set) == 2


class TestPowerCapacityRepresentation:
    """Test string representation of PowerCapacity."""

    def test_power_capacity_string_representation(self):
        """Test that PowerCapacity has readable string representation."""
        power_capacity = PowerCapacity(kilowatts=50.0)

        string_repr = str(power_capacity)

        assert "50.0" in string_repr
        assert "PowerCapacity" in string_repr

    def test_power_capacity_repr(self):
        """Test that PowerCapacity has useful repr."""
        power_capacity = PowerCapacity(kilowatts=150.5)

        repr_str = repr(power_capacity)

        assert "PowerCapacity" in repr_str
        assert "150.5" in repr_str


class TestPowerCapacityEdgeCases:
    """Test edge cases and boundary values."""

    def test_power_capacity_with_very_small_decimal(self):
        """Test power capacity with very small decimal value."""
        power_capacity = PowerCapacity(kilowatts=0.00001)

        assert power_capacity.kilowatts == 0.00001
        assert power_capacity.is_fast_charging() is False

    def test_power_capacity_boundary_at_49_9999(self):
        """Test boundary just below fast charging threshold."""
        power_capacity = PowerCapacity(kilowatts=49.9999)

        assert power_capacity.is_fast_charging() is False

    def test_power_capacity_boundary_at_50_0001(self):
        """Test boundary just above fast charging threshold."""
        power_capacity = PowerCapacity(kilowatts=50.0001)

        assert power_capacity.is_fast_charging() is True

    def test_power_capacity_at_999_9999(self):
        """Test power capacity just below maximum."""
        power_capacity = PowerCapacity(kilowatts=999.9999)

        assert power_capacity.kilowatts == 999.9999
        assert power_capacity.is_fast_charging() is True

    def test_integer_power_capacity(self):
        """Test that integer values work correctly."""
        power_capacity = PowerCapacity(kilowatts=100)

        assert power_capacity.kilowatts == 100
        assert isinstance(power_capacity.kilowatts, (int, float))


class TestPowerCapacityTypeSafety:
    """Test type safety and invalid inputs."""

    def test_power_capacity_accepts_integer(self):
        """Test that PowerCapacity accepts integer values."""
        power_capacity = PowerCapacity(kilowatts=50)

        assert power_capacity.kilowatts == 50

    def test_power_capacity_accepts_float(self):
        """Test that PowerCapacity accepts float values."""
        power_capacity = PowerCapacity(kilowatts=50.5)

        assert power_capacity.kilowatts == 50.5
