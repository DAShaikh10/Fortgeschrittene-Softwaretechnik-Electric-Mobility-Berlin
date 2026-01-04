"""
Unit Tests for ChargingStation Entity.

Test categories:
- Entity creation and initialization
- Business rules (fast charging, categorization)
- PowerCapacity integration
- Edge cases and boundary values
"""

# pylint: disable=redefined-outer-name  # pytest fixtures redefine names

import pytest

from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PowerCapacity


class TestChargingStationCreation:
    """Test ChargingStation entity creation and initialization."""

    def test_create_charging_station_with_valid_attributes(self):
        """Test creating a charging station with valid attributes."""
        station = ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_kw=50.0)

        assert station.postal_code.value == "10115"
        assert station.latitude == 52.5200
        assert station.longitude == 13.4050
        assert station.power_capacity.kilowatts == 50.0

    def test_create_charging_station_with_zero_power(self):
        """Test creating a charging station with zero power."""
        station = ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_kw=0.0)

        assert station.power_capacity.kilowatts == 0.0

    def test_create_charging_station_with_maximum_power(self):
        """Test creating a charging station with maximum power (1000 kW)."""
        station = ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_kw=1000.0)

        assert station.power_capacity.kilowatts == 1000.0

    def test_charging_station_power_capacity_is_value_object(self):
        """Test that power_capacity is a PowerCapacity value object."""
        station = ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_kw=50.0)

        assert isinstance(station.power_capacity, PowerCapacity)

    def test_create_charging_station_with_negative_power_raises_error(self):
        """Test that creating a station with negative power raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity cannot be negative"):
            ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_kw=-10.0)

    def test_create_charging_station_exceeding_maximum_power_raises_error(self):
        """Test that creating a station with power > 1000 kW raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity exceeds maximum reasonable value"):
            ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_kw=1500.0)


class TestChargingStationFastChargingBusinessRule:
    """Test is_fast_charger() business rule."""

    def test_is_fast_charger_returns_false_for_zero_power(self):
        """Test that 0 kW station is not a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 0.0)

        assert station.is_fast_charger() is False

    def test_is_fast_charger_returns_false_for_normal_charging(self):
        """Test that 22 kW station (normal charging) is not a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 22.0)

        assert station.is_fast_charger() is False

    def test_is_fast_charger_returns_false_just_below_threshold(self):
        """Test that 49.9 kW station is not a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 49.9)

        assert station.is_fast_charger() is False

    def test_is_fast_charger_returns_true_at_threshold(self):
        """Test that exactly 50 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.0)

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_just_above_threshold(self):
        """Test that 50.1 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.1)

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_for_fast_charging(self):
        """Test that 150 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 150.0)

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_for_ultra_fast_charging(self):
        """Test that 350 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 350.0)

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_for_maximum_power(self):
        """Test that 1000 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, 1000.0)

        assert station.is_fast_charger() is True


class TestChargingStationCategoryBusinessRule:
    """Test get_charging_category() business rule."""

    def test_get_charging_category_returns_normal_for_zero_power(self):
        """Test that 0 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, 0.0)

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_normal_for_low_power(self):
        """Test that 11 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, 11.0)

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_normal_for_typical_home_charging(self):
        """Test that 22 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, 22.0)

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_normal_just_below_fast_threshold(self):
        """Test that 49.9 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, 49.9)

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_fast_at_threshold(self):
        """Test that exactly 50 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.0)

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_fast_just_above_threshold(self):
        """Test that 50.1 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.1)

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_fast_for_typical_dc_charging(self):
        """Test that 100 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, 100.0)

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_fast_just_below_ultra_threshold(self):
        """Test that 149.9 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, 149.9)

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_ultra_at_threshold(self):
        """Test that exactly 150 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, 150.0)

        assert station.get_charging_category() == "ULTRA"

    def test_get_charging_category_returns_ultra_just_above_threshold(self):
        """Test that 150.1 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, 150.1)

        assert station.get_charging_category() == "ULTRA"

    def test_get_charging_category_returns_ultra_for_high_power(self):
        """Test that 350 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, 350.0)

        assert station.get_charging_category() == "ULTRA"

    def test_get_charging_category_returns_ultra_for_maximum_power(self):
        """Test that 1000 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, 1000.0)

        assert station.get_charging_category() == "ULTRA"


class TestChargingStationGeographicData:
    """Test geographic data handling."""

    def test_charging_station_stores_postal_code(self):
        """Test that postal code is stored correctly."""
        station = ChargingStation("12345", 52.5200, 13.4050, 50.0)

        assert station.postal_code.value == "12345"

    def test_charging_station_stores_latitude(self):
        """Test that latitude is stored correctly."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.0)

        assert station.latitude == 52.5200

    def test_charging_station_stores_longitude(self):
        """Test that longitude is stored correctly."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.0)

        assert station.longitude == 13.4050

    def test_charging_station_with_negative_latitude(self):
        """Test that negative latitude is accepted."""
        station = ChargingStation("10115", -52.5200, 13.4050, 50.0)

        assert station.latitude == -52.5200

    def test_charging_station_with_negative_longitude(self):
        """Test that negative longitude is accepted."""
        station = ChargingStation("10115", 52.5200, -13.4050, 50.0)

        assert station.longitude == -13.4050


class TestChargingStationBoundaryValues:
    """Test boundary values and edge cases."""

    def test_charging_station_at_fast_charging_boundary(self):
        """Test station exactly at fast charging boundary."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.0)

        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "FAST"

    def test_charging_station_at_ultra_charging_boundary(self):
        """Test station exactly at ultra charging boundary."""
        station = ChargingStation("10115", 52.5200, 13.4050, 150.0)

        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "ULTRA"

    def test_charging_station_with_fractional_power(self):
        """Test station with fractional power value."""
        station = ChargingStation("10115", 52.5200, 13.4050, 75.5)

        assert station.power_capacity.kilowatts == 75.5
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "FAST"

    def test_charging_station_with_very_small_power(self):
        """Test station with very small power value."""
        station = ChargingStation("10115", 52.5200, 13.4050, 0.001)

        assert station.power_capacity.kilowatts == 0.001
        assert station.is_fast_charger() is False
        assert station.get_charging_category() == "NORMAL"


class TestChargingStationIntegration:
    """Test integration between ChargingStation and PowerCapacity."""

    def test_charging_station_delegates_to_power_capacity_for_fast_charging(self):
        """Test that is_fast_charger() uses PowerCapacity.is_fast_charging()."""
        station = ChargingStation("10115", 52.5200, 13.4050, 75.0)

        # Both should return the same result
        assert station.is_fast_charger() == station.power_capacity.is_fast_charging()

    def test_charging_station_category_consistent_with_power_capacity(self):
        """Test that category is consistent with power capacity value."""
        # Test NORMAL
        station_normal = ChargingStation("10115", 52.5200, 13.4050, 22.0)
        assert station_normal.get_charging_category() == "NORMAL"
        assert station_normal.power_capacity.kilowatts < 50.0

        # Test FAST
        station_fast = ChargingStation("10115", 52.5200, 13.4050, 100.0)
        assert station_fast.get_charging_category() == "FAST"
        assert 50.0 <= station_fast.power_capacity.kilowatts < 150.0

        # Test ULTRA
        station_ultra = ChargingStation("10115", 52.5200, 13.4050, 350.0)
        assert station_ultra.get_charging_category() == "ULTRA"
        assert station_ultra.power_capacity.kilowatts >= 150.0

    def test_multiple_stations_with_different_powers(self):
        """Test creating multiple stations with different power capacities."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, 11.0)
        station2 = ChargingStation("10115", 52.5201, 13.4051, 50.0)
        station3 = ChargingStation("10115", 52.5202, 13.4052, 150.0)

        assert station1.get_charging_category() == "NORMAL"
        assert station2.get_charging_category() == "FAST"
        assert station3.get_charging_category() == "ULTRA"

        assert station1.is_fast_charger() is False
        assert station2.is_fast_charger() is True
        assert station3.is_fast_charger() is True


class TestChargingStationRealWorldScenarios:
    """Test real-world charging station scenarios."""

    def test_typical_home_wallbox(self):
        """Test typical home wallbox (11 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, 11.0)

        assert station.power_capacity.kilowatts == 11.0
        assert station.is_fast_charger() is False
        assert station.get_charging_category() == "NORMAL"

    def test_typical_public_ac_charger(self):
        """Test typical public AC charger (22 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, 22.0)

        assert station.power_capacity.kilowatts == 22.0
        assert station.is_fast_charger() is False
        assert station.get_charging_category() == "NORMAL"

    def test_typical_dc_fast_charger(self):
        """Test typical DC fast charger (50 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, 50.0)

        assert station.power_capacity.kilowatts == 50.0
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "FAST"

    def test_typical_highway_fast_charger(self):
        """Test typical highway fast charger (150 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, 150.0)

        assert station.power_capacity.kilowatts == 150.0
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "ULTRA"

    def test_ultra_fast_charger_350kw(self):
        """Test ultra-fast charger (350 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, 350.0)

        assert station.power_capacity.kilowatts == 350.0
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "ULTRA"
