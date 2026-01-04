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
        station = ChargingStation(
            postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(50.0)
        )

        assert station.postal_code.value == "10115"
        assert station.latitude == 52.5200
        assert station.longitude == 13.4050
        assert station.power_capacity.kilowatts == 50.0

    def test_create_charging_station_with_zero_power(self):
        """Test creating a charging station with zero power."""
        station = ChargingStation(
            postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(0.0)
        )

        assert station.power_capacity.kilowatts == 0.0

    def test_create_charging_station_with_maximum_power(self):
        """Test creating a charging station with maximum power (1000 kW)."""
        station = ChargingStation(
            postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(1000.0)
        )

        assert station.power_capacity.kilowatts == 1000.0

    def test_charging_station_power_capacity_is_value_object(self):
        """Test that power_capacity is a PowerCapacity value object."""
        station = ChargingStation(
            postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(50.0)
        )

        assert isinstance(station.power_capacity, PowerCapacity)

    def test_create_charging_station_with_negative_power_raises_error(self):
        """Test that creating a station with negative power raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity cannot be negative"):
            ChargingStation(
                postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(-10.0)
            )

    def test_create_charging_station_exceeding_maximum_power_raises_error(self):
        """Test that creating a station with power > 1000 kW raises ValueError."""
        with pytest.raises(ValueError, match="Power capacity exceeds maximum reasonable value"):
            ChargingStation(
                postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(1500.0)
            )

    def test_create_charging_station_with_float_auto_converts_to_power_capacity(self):
        """Test that passing a float automatically converts to PowerCapacity."""
        station = ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=75.0)

        assert isinstance(station.power_capacity, PowerCapacity)
        assert station.power_capacity.kilowatts == 75.0


class TestChargingStationFastChargingBusinessRule:
    """Test is_fast_charger() business rule."""

    def test_is_fast_charger_returns_false_for_zero_power(self):
        """Test that 0 kW station is not a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(0.0))

        assert station.is_fast_charger() is False

    def test_is_fast_charger_returns_false_for_normal_charging(self):
        """Test that 22 kW station (normal charging) is not a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(22.0))

        assert station.is_fast_charger() is False

    def test_is_fast_charger_returns_false_just_below_threshold(self):
        """Test that 49.9 kW station is not a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(49.9))

        assert station.is_fast_charger() is False

    def test_is_fast_charger_returns_true_at_threshold(self):
        """Test that exactly 50 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_just_above_threshold(self):
        """Test that 50.1 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.1))

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_for_fast_charging(self):
        """Test that 150 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(150.0))

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_for_ultra_fast_charging(self):
        """Test that 350 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(350.0))

        assert station.is_fast_charger() is True

    def test_is_fast_charger_returns_true_for_maximum_power(self):
        """Test that 1000 kW station is a fast charger."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(1000.0))

        assert station.is_fast_charger() is True


class TestChargingStationCategoryBusinessRule:
    """Test get_charging_category() business rule."""

    def test_get_charging_category_returns_normal_for_zero_power(self):
        """Test that 0 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(0.0))

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_normal_for_low_power(self):
        """Test that 11 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(11.0))

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_normal_for_typical_home_charging(self):
        """Test that 22 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(22.0))

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_normal_just_below_fast_threshold(self):
        """Test that 49.9 kW station is categorized as NORMAL."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(49.9))

        assert station.get_charging_category() == "NORMAL"

    def test_get_charging_category_returns_fast_at_threshold(self):
        """Test that exactly 50 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_fast_just_above_threshold(self):
        """Test that 50.1 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.1))

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_fast_for_typical_dc_charging(self):
        """Test that 100 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(100.0))

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_fast_just_below_ultra_threshold(self):
        """Test that 149.9 kW station is categorized as FAST."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(149.9))

        assert station.get_charging_category() == "FAST"

    def test_get_charging_category_returns_ultra_at_threshold(self):
        """Test that exactly 150 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(150.0))

        assert station.get_charging_category() == "ULTRA"

    def test_get_charging_category_returns_ultra_just_above_threshold(self):
        """Test that 150.1 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(150.1))

        assert station.get_charging_category() == "ULTRA"

    def test_get_charging_category_returns_ultra_for_high_power(self):
        """Test that 350 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(350.0))

        assert station.get_charging_category() == "ULTRA"

    def test_get_charging_category_returns_ultra_for_maximum_power(self):
        """Test that 1000 kW station is categorized as ULTRA."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(1000.0))

        assert station.get_charging_category() == "ULTRA"


class TestChargingStationGeographicData:
    """Test geographic data handling."""

    def test_charging_station_stores_postal_code(self):
        """Test that postal code is stored correctly."""
        station = ChargingStation("12345", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.postal_code.value == "12345"

    def test_charging_station_stores_latitude(self):
        """Test that latitude is stored correctly."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.latitude == 52.5200

    def test_charging_station_stores_longitude(self):
        """Test that longitude is stored correctly."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.longitude == 13.4050

    def test_charging_station_with_negative_latitude(self):
        """Test that negative latitude is accepted."""
        station = ChargingStation("10115", -52.5200, 13.4050, PowerCapacity(50.0))

        assert station.latitude == -52.5200

    def test_charging_station_with_negative_longitude(self):
        """Test that negative longitude is accepted."""
        station = ChargingStation("10115", 52.5200, -13.4050, PowerCapacity(50.0))

        assert station.longitude == -13.4050


class TestChargingStationBoundaryValues:
    """Test boundary values and edge cases."""

    def test_charging_station_at_fast_charging_boundary(self):
        """Test station exactly at fast charging boundary."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "FAST"

    def test_charging_station_at_ultra_charging_boundary(self):
        """Test station exactly at ultra charging boundary."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(150.0))

        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "ULTRA"

    def test_charging_station_with_fractional_power(self):
        """Test station with fractional power value."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(75.5))

        assert station.power_capacity.kilowatts == 75.5
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "FAST"

    def test_charging_station_with_very_small_power(self):
        """Test station with very small power value."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(0.001))

        assert station.power_capacity.kilowatts == 0.001
        assert station.is_fast_charger() is False
        assert station.get_charging_category() == "NORMAL"


class TestChargingStationIntegration:
    """Test integration between ChargingStation and PowerCapacity."""

    def test_charging_station_delegates_to_power_capacity_for_fast_charging(self):
        """Test that is_fast_charger() uses PowerCapacity.is_fast_charging()."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(75.0))

        # Both should return the same result
        assert station.is_fast_charger() == station.power_capacity.is_fast_charging()

    def test_charging_station_category_consistent_with_power_capacity(self):
        """Test that category is consistent with power capacity value."""
        # Test NORMAL
        station_normal = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(22.0))
        assert station_normal.get_charging_category() == "NORMAL"
        assert station_normal.power_capacity.kilowatts < 50.0

        # Test FAST
        station_fast = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(100.0))
        assert station_fast.get_charging_category() == "FAST"
        assert 50.0 <= station_fast.power_capacity.kilowatts < 150.0

        # Test ULTRA
        station_ultra = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(350.0))
        assert station_ultra.get_charging_category() == "ULTRA"
        assert station_ultra.power_capacity.kilowatts >= 150.0

    def test_multiple_stations_with_different_powers(self):
        """Test creating multiple stations with different power capacities."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(11.0))
        station2 = ChargingStation("10115", 52.5201, 13.4051, PowerCapacity(50.0))
        station3 = ChargingStation("10115", 52.5202, 13.4052, PowerCapacity(150.0))

        assert station1.get_charging_category() == "NORMAL"
        assert station2.get_charging_category() == "FAST"
        assert station3.get_charging_category() == "ULTRA"

        assert station1.is_fast_charger() is False
        assert station2.is_fast_charger() is True
        assert station3.is_fast_charger() is True


class TestChargingStationEquality:
    """Test entity equality based on identity."""

    def test_two_stations_with_same_id_are_equal(self):
        """Test that two stations with the same ID are equal."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))
        station2 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        # Same attributes produce same ID
        assert station1.id == station2.id
        assert station1 == station2

    def test_two_stations_with_different_ids_are_not_equal(self):
        """Test that two stations with different IDs are not equal."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))
        station2 = ChargingStation("10115", 52.5201, 13.4051, PowerCapacity(50.0))  # Different coordinates

        assert station1.id != station2.id
        assert station1 != station2

    def test_station_not_equal_to_non_station_object(self):
        """Test that a station is not equal to a non-ChargingStation object."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station != "not a station"
        assert station != 123
        assert station is not None
        assert station != {"id": station.id}

    def test_station_with_custom_id_equality(self):
        """Test equality when stations have custom IDs."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0), station_id="custom-id-1")
        station2 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0), station_id="custom-id-1")
        station3 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0), station_id="custom-id-2")

        assert station1 == station2
        assert station1 != station3


class TestChargingStationHashing:
    """Test entity hashing for use in sets and dictionaries."""

    def test_station_is_hashable(self):
        """Test that ChargingStation can be hashed."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        hash_value = hash(station)
        assert isinstance(hash_value, int)

    def test_stations_with_same_id_have_same_hash(self):
        """Test that stations with the same ID have the same hash."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))
        station2 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert hash(station1) == hash(station2)

    def test_stations_can_be_used_in_set(self):
        """Test that ChargingStation can be used in a set."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))
        station2 = ChargingStation("10115", 52.5201, 13.4051, PowerCapacity(50.0))
        station3 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))  # Same as station1

        station_set = {station1, station2, station3}

        # station1 and station3 are equal, so only 2 unique stations
        assert len(station_set) == 2
        assert station1 in station_set
        assert station2 in station_set

    def test_stations_can_be_used_as_dict_keys(self):
        """Test that ChargingStation can be used as dictionary keys."""
        station1 = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))
        station2 = ChargingStation("10115", 52.5201, 13.4051, PowerCapacity(100.0))

        station_dict = {station1: "Station A", station2: "Station B"}

        assert station_dict[station1] == "Station A"
        assert station_dict[station2] == "Station B"

    def test_hash_consistency_after_multiple_calls(self):
        """Test that hash value is consistent across multiple calls."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        hash1 = hash(station)
        hash2 = hash(station)
        hash3 = hash(station)

        assert hash1 == hash2 == hash3


class TestChargingStationRealWorldScenarios:
    """Test real-world charging station scenarios."""

    def test_typical_home_wallbox(self):
        """Test typical home wallbox (11 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(11.0))

        assert station.power_capacity.kilowatts == 11.0
        assert station.is_fast_charger() is False
        assert station.get_charging_category() == "NORMAL"

    def test_typical_public_ac_charger(self):
        """Test typical public AC charger (22 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(22.0))

        assert station.power_capacity.kilowatts == 22.0
        assert station.is_fast_charger() is False
        assert station.get_charging_category() == "NORMAL"

    def test_typical_dc_fast_charger(self):
        """Test typical DC fast charger (50 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(50.0))

        assert station.power_capacity.kilowatts == 50.0
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "FAST"

    def test_typical_highway_fast_charger(self):
        """Test typical highway fast charger (150 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(150.0))

        assert station.power_capacity.kilowatts == 150.0
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "ULTRA"

    def test_ultra_fast_charger_350kw(self):
        """Test ultra-fast charger (350 kW)."""
        station = ChargingStation("10115", 52.5200, 13.4050, PowerCapacity(350.0))

        assert station.power_capacity.kilowatts == 350.0
        assert station.is_fast_charger() is True
        assert station.get_charging_category() == "ULTRA"
