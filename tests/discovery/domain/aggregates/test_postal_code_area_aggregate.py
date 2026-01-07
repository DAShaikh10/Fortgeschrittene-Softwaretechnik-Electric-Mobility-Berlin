"""
Unit Tests for PostalCodeAreaAggregate.

Test categories:
- Factory method tests
- Query tests
- Business rule tests
- Event handling tests
- Edge cases and validation
"""

# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from src.shared.domain.entities import ChargingStation
from src.shared.domain.enums import CoverageLevel
from src.shared.domain.events import (
    StationSearchPerformedEvent,
    StationSearchFailedEvent,
    NoStationsFoundEvent,
    StationsFoundEvent,
)
from src.discovery.domain.aggregates import PostalCodeAreaAggregate


class TestPostalCodeAreaAggregateFactoryMethods:
    """Test factory methods for creating aggregates."""

    def test_create_returns_aggregate_with_empty_stations(self, valid_postal_code):
        """Test create factory method returns aggregate with no stations."""
        postal_code = valid_postal_code
        aggregate = PostalCodeAreaAggregate.create(postal_code)

        assert isinstance(aggregate, PostalCodeAreaAggregate)
        assert aggregate.get_postal_code() == postal_code
        assert aggregate.get_station_count() == 0
        assert aggregate.get_stations() == []

    def test_create_with_stations_returns_aggregate_with_stations(self, valid_postal_code, mock_charging_station):
        """Test create_with_stations factory method."""
        stations = [mock_charging_station, mock_charging_station]

        aggregate = PostalCodeAreaAggregate.create_with_stations(valid_postal_code, stations)

        assert aggregate.get_postal_code() == valid_postal_code
        assert aggregate.get_station_count() == 2

    def test_create_with_stations_validates_station_types(self, valid_postal_code):
        """Test that create_with_stations validates all items are ChargingStation entities."""
        invalid_stations = [Mock(spec=ChargingStation), "not a station", Mock(spec=ChargingStation)]

        with pytest.raises(ValueError, match="All items must be ChargingStation entities"):
            PostalCodeAreaAggregate.create_with_stations(valid_postal_code, invalid_stations)

    def test_create_with_stations_creates_copy_of_list(self, valid_postal_code, mock_charging_station):
        """Test that create_with_stations creates a copy of the stations list."""
        original_stations = [mock_charging_station]
        aggregate = PostalCodeAreaAggregate.create_with_stations(valid_postal_code, original_stations)

        # Modifying original should not affect aggregate
        original_stations.append(mock_charging_station)

        assert aggregate.get_station_count() == 1


class TestPostalCodeAreaAggregateQueries:
    """Test query methods."""

    def test_get_postal_code_returns_postal_code(self, valid_postal_code):
        """Test get_postal_code returns the postal code value object."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.get_postal_code() == valid_postal_code

    def test_get_stations_returns_copy_of_stations_list(self, valid_postal_code, mock_charging_station):
        """Test get_stations returns a copy to protect encapsulation."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)

        stations1 = aggregate.get_stations()
        stations2 = aggregate.get_stations()

        assert stations1 == stations2
        assert stations1 is not stations2

    def test_get_stations_modifications_dont_affect_aggregate(self, valid_postal_code, mock_charging_station):
        """Test that modifying returned stations list doesn't affect aggregate."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)

        stations = aggregate.get_stations()
        stations.append(mock_charging_station)

        assert aggregate.get_station_count() == 1

    def test_get_station_count_returns_correct_count(self, valid_postal_code, mock_charging_station):
        """Test get_station_count returns the correct number."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.get_station_count() == 0

        aggregate.add_station(mock_charging_station)
        assert aggregate.get_station_count() == 1

        aggregate.add_station(mock_charging_station)
        assert aggregate.get_station_count() == 2

    def test_get_fast_charger_count_counts_fast_chargers(
        self, valid_postal_code, mock_charging_station, mock_slow_station
    ):
        """Test get_fast_charger_count counts only fast chargers (>=50kW)."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.add_station(mock_charging_station)  # Fast
        aggregate.add_station(mock_slow_station)  # Slow
        aggregate.add_station(mock_charging_station)  # Fast

        assert aggregate.get_fast_charger_count() == 2

    def test_get_total_capacity_kw_sums_all_power(self, valid_postal_code):
        """Test get_total_capacity_kw sums power capacity across all stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        station1 = Mock(spec=ChargingStation)
        power_capacity_1 = Mock()
        power_capacity_1.kilowatts = 50.0
        station1.power_capacity = power_capacity_1

        station2 = Mock(spec=ChargingStation)
        power_capacity_2 = Mock()
        power_capacity_2.kilowatts = 22.0
        station2.power_capacity = power_capacity_2

        station3 = Mock(spec=ChargingStation)
        power_capacity_3 = Mock()
        power_capacity_3.kilowatts = 11.0
        station3.power_capacity = power_capacity_3

        aggregate.add_station(station1)
        aggregate.add_station(station2)
        aggregate.add_station(station3)

        assert aggregate.get_total_capacity_kw() == 83.0

    def test_get_total_capacity_kw_returns_zero_for_no_stations(self, valid_postal_code):
        """Test get_total_capacity_kw returns 0.0 when no stations exist."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.get_total_capacity_kw() == 0.0

    def test_get_average_power_kw_calculates_average(self, valid_postal_code):
        """Test get_average_power_kw calculates correct average."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        station1 = Mock(spec=ChargingStation)
        power_capacity_1 = Mock()
        power_capacity_1.kilowatts = 60.0
        station1.power_capacity = power_capacity_1

        station2 = Mock(spec=ChargingStation)
        power_capacity_2 = Mock()
        power_capacity_2.kilowatts = 40.0
        station2.power_capacity = power_capacity_2

        station3 = Mock(spec=ChargingStation)
        power_capacity_3 = Mock()
        power_capacity_3.kilowatts = 50.0
        station3.power_capacity = power_capacity_3

        aggregate.add_station(station1)
        aggregate.add_station(station2)
        aggregate.add_station(station3)

        assert aggregate.get_average_power_kw() == 50.0

    def test_get_average_power_kw_returns_zero_for_no_stations(self, valid_postal_code):
        """Test get_average_power_kw returns 0.0 when no stations exist."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.get_average_power_kw() == 0.0

    def test_get_stations_by_category_groups_correctly(self, valid_postal_code):
        """Test get_stations_by_category groups stations by charging category."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        fast1 = Mock(spec=ChargingStation)
        fast1.get_charging_category = Mock(return_value="FAST")
        fast2 = Mock(spec=ChargingStation)
        fast2.get_charging_category = Mock(return_value="FAST")
        normal = Mock(spec=ChargingStation)
        normal.get_charging_category = Mock(return_value="NORMAL")

        aggregate.add_station(fast1)
        aggregate.add_station(normal)
        aggregate.add_station(fast2)

        categories = aggregate.get_stations_by_category()

        assert len(categories["FAST"]) == 2
        assert len(categories["NORMAL"]) == 1
        assert fast1 in categories["FAST"]
        assert fast2 in categories["FAST"]
        assert normal in categories["NORMAL"]


class TestPostalCodeAreaAggregateCommands:
    """Test command methods that modify state."""

    def test_add_station_adds_charging_station(self, valid_postal_code, mock_charging_station):
        """Test add_station adds a valid ChargingStation."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.add_station(mock_charging_station)

        assert aggregate.get_station_count() == 1
        assert mock_charging_station in aggregate.get_stations()

    def test_add_station_validates_type(self, valid_postal_code):
        """Test add_station raises ValueError for non-ChargingStation objects."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        with pytest.raises(ValueError, match="Must be a ChargingStation entity"):
            aggregate.add_station("not a station")

    def test_add_multiple_stations(self, valid_postal_code, mock_charging_station, mock_slow_station):
        """Test adding multiple stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.add_station(mock_charging_station)
        aggregate.add_station(mock_slow_station)
        aggregate.add_station(mock_charging_station)

        assert aggregate.get_station_count() == 3


class TestPostalCodeAreaAggregateBusinessRules:
    """Test business rule methods."""

    def test_has_fast_charging_returns_true_when_fast_chargers_exist(self, valid_postal_code, mock_charging_station):
        """Test has_fast_charging returns True when at least one fast charger exists."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)

        assert aggregate.has_fast_charging() is True

    def test_has_fast_charging_returns_false_when_no_fast_chargers(self, valid_postal_code, mock_slow_station):
        """Test has_fast_charging returns False when no fast chargers exist."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_slow_station)

        assert aggregate.has_fast_charging() is False

    def test_has_fast_charging_returns_false_for_empty_aggregate(self, valid_postal_code):
        """Test has_fast_charging returns False when no stations exist."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.has_fast_charging() is False

    def test_is_well_equipped_true_with_5_or_more_stations(self, valid_postal_code, mock_slow_station):
        """Test is_well_equipped returns True with >= 5 stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        for _ in range(5):
            aggregate.add_station(mock_slow_station)

        assert aggregate.is_well_equipped() is True

    def test_is_well_equipped_true_with_2_or_more_fast_chargers(self, valid_postal_code, mock_charging_station):
        """Test is_well_equipped returns True with >= 2 fast chargers."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.add_station(mock_charging_station)
        aggregate.add_station(mock_charging_station)

        assert aggregate.is_well_equipped() is True

    def test_is_well_equipped_false_with_insufficient_criteria(self, valid_postal_code, mock_slow_station):
        """Test is_well_equipped returns False when criteria not met."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.add_station(mock_slow_station)
        aggregate.add_station(mock_slow_station)

        assert aggregate.is_well_equipped() is False

    def test_get_coverage_level_no_coverage(self, valid_postal_code):
        """Test get_coverage_level returns NO_COVERAGE when no stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.get_coverage_level() == CoverageLevel.NO_COVERAGE

    def test_get_coverage_level_poor(self, valid_postal_code, mock_slow_station):
        """Test get_coverage_level returns POOR for < 5 stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.add_station(mock_slow_station)
        aggregate.add_station(mock_slow_station)

        assert aggregate.get_coverage_level() == CoverageLevel.POOR

    def test_get_coverage_level_adequate(self, valid_postal_code, mock_slow_station):
        """Test get_coverage_level returns ADEQUATE for 5+ stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        for _ in range(5):
            aggregate.add_station(mock_slow_station)

        assert aggregate.get_coverage_level() == CoverageLevel.ADEQUATE

    def test_get_coverage_level_good(self, valid_postal_code, mock_charging_station, mock_slow_station):
        """Test get_coverage_level returns GOOD for 10+ stations with 2+ fast chargers."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        for _ in range(8):
            aggregate.add_station(mock_slow_station)
        for _ in range(2):
            aggregate.add_station(mock_charging_station)

        assert aggregate.get_coverage_level() == CoverageLevel.GOOD

    def test_get_coverage_level_excellent(self, valid_postal_code, mock_charging_station, mock_slow_station):
        """Test get_coverage_level returns EXCELLENT for 20+ stations with 5+ fast chargers."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        for _ in range(15):
            aggregate.add_station(mock_slow_station)
        for _ in range(5):
            aggregate.add_station(mock_charging_station)

        assert aggregate.get_coverage_level() == CoverageLevel.EXCELLENT


class TestPostalCodeAreaAggregateDataConversion:
    """Test data conversion methods."""

    @staticmethod
    def to_dict_helper(aggregate: PostalCodeAreaAggregate) -> dict:
        """Map aggregate to dict via public queries (no domain internals exposure)."""
        return {
            "postal_code": aggregate.get_postal_code().value,
            "station_count": aggregate.get_station_count(),
            "fast_charger_count": aggregate.get_fast_charger_count(),
            "total_capacity_kw": aggregate.get_total_capacity_kw(),
            "average_power_kw": aggregate.get_average_power_kw(),
            "has_fast_charging": aggregate.has_fast_charging(),
            "is_well_equipped": aggregate.is_well_equipped(),
            "coverage_level": aggregate.get_coverage_level().value,
        }

    def test_to_dict_returns_correct_structure(self, valid_postal_code, mock_charging_station, mock_slow_station):
        """Test to_dict returns dictionary with all business metrics."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)
        aggregate.add_station(mock_slow_station)

        result = self.to_dict_helper(aggregate)

        assert result["postal_code"] == "10115"
        assert result["station_count"] == 2
        assert result["fast_charger_count"] == 1
        assert "total_capacity_kw" in result
        assert "average_power_kw" in result
        assert result["has_fast_charging"] is True
        assert result["is_well_equipped"] is False
        assert result["coverage_level"] == "POOR"

    def test_to_dict_handles_empty_aggregate(self, valid_postal_code):
        """Test to_dict works correctly for empty aggregate."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        result = self.to_dict_helper(aggregate)

        assert result["postal_code"] == "10115"
        assert result["station_count"] == 0
        assert result["fast_charger_count"] == 0
        assert result["total_capacity_kw"] == 0.0
        assert result["average_power_kw"] == 0.0
        assert result["has_fast_charging"] is False
        assert result["is_well_equipped"] is False
        assert result["coverage_level"] == "NO_COVERAGE"


class TestPostalCodeAreaAggregateEventHandling:
    """Test domain event handling."""

    def test_perform_search_adds_domain_event(self, valid_postal_code):
        """Test perform_search creates and adds a domain event."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.perform_search({"postal_code": "10115"})

        assert aggregate.has_domain_events() is True
        assert aggregate.get_event_count() == 1

    def test_perform_search_with_no_parameters(self, valid_postal_code):
        """Test perform_search works with None parameters."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.perform_search()

        assert aggregate.has_domain_events() is True

    def test_perform_search_event_contains_correct_data(self, valid_postal_code, mock_charging_station):
        """Test perform_search event contains correct postal code and station count."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)
        aggregate.add_station(mock_charging_station)

        aggregate.perform_search({"postal_code": "10115"})

        events = aggregate.get_domain_events()
        event = events[0]

        assert isinstance(event, StationSearchPerformedEvent)
        assert event.postal_code == valid_postal_code
        assert event.stations_found == 2

    def test_fail_search_adds_domain_event(self, valid_postal_code):
        """Test fail_search creates and adds a domain event."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.fail_search(error_message="Test error")

        assert aggregate.has_domain_events() is True
        assert aggregate.get_event_count() == 1

    def test_fail_search_event_contains_correct_data(self, valid_postal_code):
        """Test fail_search event contains correct error information."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        error_message = "Database connection failed"
        error_type = "ConnectionError"

        aggregate.fail_search(error_message=error_message, error_type=error_type)

        events = aggregate.get_domain_events()
        event = events[0]

        assert isinstance(event, StationSearchFailedEvent)
        assert event.postal_code == valid_postal_code
        assert event.error_message == error_message
        assert event.error_type == error_type

    def test_fail_search_without_error_type(self, valid_postal_code):
        """Test fail_search works without error_type parameter."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.fail_search(error_message="Unknown error")

        events = aggregate.get_domain_events()
        event = events[0]

        assert isinstance(event, StationSearchFailedEvent)
        assert event.error_type is None

    def test_record_no_stations_adds_domain_event(self, valid_postal_code):
        """Test record_no_stations creates and adds a domain event."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.record_no_stations()

        assert aggregate.has_domain_events() is True
        assert aggregate.get_event_count() == 1

    def test_record_no_stations_event_contains_correct_data(self, valid_postal_code):
        """Test record_no_stations event contains correct postal code."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        aggregate.record_no_stations()

        events = aggregate.get_domain_events()
        event = events[0]

        assert isinstance(event, NoStationsFoundEvent)
        assert event.postal_code == valid_postal_code

    def test_record_no_stations_for_empty_aggregate(self, valid_postal_code):
        """Test record_no_stations works correctly for aggregate with zero stations."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        assert aggregate.get_station_count() == 0
        aggregate.record_no_stations()

        events = aggregate.get_domain_events()
        assert len(events) == 1

    def test_record_stations_found_adds_domain_event(self, valid_postal_code, mock_charging_station):
        """Test record_stations_found creates and adds a domain event."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)

        aggregate.record_stations_found()

        assert aggregate.has_domain_events() is True
        assert aggregate.get_event_count() == 1

    def test_record_stations_found_event_contains_correct_data(self, valid_postal_code, mock_charging_station):
        """Test record_stations_found event contains correct information."""
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)
        aggregate.add_station(mock_charging_station)
        aggregate.add_station(mock_charging_station)
        aggregate.add_station(mock_charging_station)

        aggregate.record_stations_found()

        events = aggregate.get_domain_events()
        event = events[0]

        assert isinstance(event, StationsFoundEvent)
        assert event.postal_code == valid_postal_code
        assert event.stations_found == 3


class TestPostalCodeAreaAggregateIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow_with_multiple_stations(self, valid_postal_code):
        """Test complete workflow: create, add stations, query, check rules."""
        # Create aggregate
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        # Add various stations
        fast1 = Mock(spec=ChargingStation)
        power_capacity_fast1 = Mock()
        power_capacity_fast1.kilowatts = 50.0
        fast1.power_capacity = power_capacity_fast1
        fast1.is_fast_charger = Mock(return_value=True)
        fast1.get_charging_category = Mock(return_value="FAST")

        fast2 = Mock(spec=ChargingStation)
        power_capacity_fast2 = Mock()
        power_capacity_fast2.kilowatts = 150.0
        fast2.power_capacity = power_capacity_fast2
        fast2.is_fast_charger = Mock(return_value=True)
        fast2.get_charging_category = Mock(return_value="ULTRA")

        normal = Mock(spec=ChargingStation)
        power_capacity_normal = Mock()
        power_capacity_normal.kilowatts = 22.0
        normal.power_capacity = power_capacity_normal
        normal.is_fast_charger = Mock(return_value=False)
        normal.get_charging_category = Mock(return_value="NORMAL")

        aggregate.add_station(fast1)
        aggregate.add_station(fast2)
        aggregate.add_station(normal)

        # Verify queries
        assert aggregate.get_station_count() == 3
        assert aggregate.get_fast_charger_count() == 2
        assert aggregate.get_total_capacity_kw() == 222.0
        assert aggregate.get_average_power_kw() == 74.0

        # Verify business rules
        assert aggregate.has_fast_charging() is True
        assert aggregate.is_well_equipped() is True
        assert aggregate.get_coverage_level() == CoverageLevel.POOR  # Only 3 stations

        # Verify event handling
        aggregate.perform_search()
        assert aggregate.has_domain_events() is True

        # Verify data conversion
        data = TestPostalCodeAreaAggregateDataConversion.to_dict_helper(aggregate)
        assert data["postal_code"] == "10115"
        assert data["station_count"] == 3

    def test_aggregate_with_exactly_coverage_boundaries(self, valid_postal_code):
        """Test coverage levels at exact boundary values."""
        # Test ADEQUATE boundary (exactly 5 stations)
        aggregate = PostalCodeAreaAggregate.create(valid_postal_code)

        slow = Mock(spec=ChargingStation)
        power_capacity_slow = Mock()
        power_capacity_slow.kilowatts = 11.0
        slow.power_capacity = power_capacity_slow
        slow.is_fast_charger = Mock(return_value=False)

        for _ in range(5):
            aggregate.add_station(slow)

        assert aggregate.get_coverage_level() == CoverageLevel.ADEQUATE
        assert aggregate.is_well_equipped() is True
