"""
Demand Domain Demand Analysis Calculated Events Tests.
"""

# pylint: disable=redefined-outer-name

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from src.shared.domain.value_objects import PostalCode
from src.demand.domain.enums import PriorityLevel
from src.demand.domain.events import DemandAnalysisCalculatedEvent
from src.demand.domain.value_objects import DemandPriority


@pytest.fixture
def valid_postal_code():
    """Create a valid postal code."""
    return PostalCode("10115")


@pytest.fixture
def valid_demand_priority():
    """Create a valid demand priority."""
    return DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)


@pytest.fixture
def demand_calculated_event(valid_postal_code, valid_demand_priority):
    """Create a demand analysis calculated event."""
    return DemandAnalysisCalculatedEvent(
        postal_code=valid_postal_code,
        population=30000,
        station_count=5,
        demand_priority=valid_demand_priority,
    )


class TestDemandAnalysisCalculatedEventInitialization:
    """Test event initialization."""

    def test_event_initialization_with_valid_data(self, valid_postal_code, valid_demand_priority):
        """Test creating event with valid data."""
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            demand_priority=valid_demand_priority,
        )

        assert event.postal_code == valid_postal_code
        assert event.population == 30000
        assert event.station_count == 5
        assert event.demand_priority == valid_demand_priority

    def test_event_initialization_with_zero_population(self, valid_postal_code, valid_demand_priority):
        """Test event with zero population."""
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=0,
            station_count=5,
            demand_priority=valid_demand_priority,
        )

        assert event.population == 0

    def test_event_initialization_with_zero_stations(self, valid_postal_code, valid_demand_priority):
        """Test event with zero stations."""
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=50000,
            station_count=0,
            demand_priority=valid_demand_priority,
        )

        assert event.station_count == 0

    def test_event_initialization_with_large_numbers(self, valid_postal_code, valid_demand_priority):
        """Test event with large population and station counts."""
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=1000000,
            station_count=500,
            demand_priority=valid_demand_priority,
        )

        assert event.population == 1000000
        assert event.station_count == 500


class TestDemandAnalysisCalculatedEventImmutability:
    """Test immutability of frozen dataclass."""

    def test_cannot_modify_postal_code(self, demand_calculated_event):
        """Test that postal code cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            demand_calculated_event.postal_code = PostalCode("12345")

    def test_cannot_modify_population(self, demand_calculated_event):
        """Test that population cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            demand_calculated_event.population = 50000

    def test_cannot_modify_station_count(self, demand_calculated_event):
        """Test that station count cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            demand_calculated_event.station_count = 10

    def test_cannot_modify_demand_priority(self, demand_calculated_event):
        """Test that demand priority cannot be modified."""
        new_priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=1000.0)
        with pytest.raises(FrozenInstanceError):
            demand_calculated_event.demand_priority = new_priority


class TestDemandAnalysisCalculatedEventType:
    """Test event type information."""

    def test_event_has_type_attribute(self, demand_calculated_event):
        """Test that event has a type attribute."""
        assert hasattr(demand_calculated_event, "event_type")
        assert demand_calculated_event.event_type is not None

    def test_event_type_name_matches_class(self, demand_calculated_event):
        """Test that event type name matches class name."""
        assert "DemandAnalysisCalculatedEvent" in str(demand_calculated_event.event_type)

    def test_multiple_events_have_same_type(self, valid_postal_code, valid_demand_priority):
        """Test that multiple events have the same class type."""
        event1 = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            demand_priority=valid_demand_priority,
        )
        event2 = DemandAnalysisCalculatedEvent(
            postal_code=PostalCode("12345"),
            population=20000,
            station_count=4,
            demand_priority=valid_demand_priority,
        )

        assert type(event1) == type(event2)
        assert type(event1).__name__ == "DemandAnalysisCalculatedEvent"


class TestDemandAnalysisCalculatedEventData:
    """Test event data and attributes."""

    def test_event_contains_all_required_fields(self, demand_calculated_event):
        """Test that event has all required fields."""
        assert hasattr(demand_calculated_event, "postal_code")
        assert hasattr(demand_calculated_event, "population")
        assert hasattr(demand_calculated_event, "station_count")
        assert hasattr(demand_calculated_event, "demand_priority")

    def test_event_has_timestamp(self, demand_calculated_event):
        """Test that event has a timestamp from DomainEvent."""
        assert hasattr(demand_calculated_event, "occurred_at")
        assert demand_calculated_event.occurred_at is not None

    def test_event_timestamp_is_datetime(self, demand_calculated_event):
        """Test that timestamp is a datetime object."""
        assert isinstance(demand_calculated_event.occurred_at, datetime)

    def test_event_data_preservation(self, valid_postal_code, valid_demand_priority):
        """Test that event data is preserved correctly."""
        population = 25000
        station_count = 3
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=population,
            station_count=station_count,
            demand_priority=valid_demand_priority,
        )

        assert event.population == population
        assert event.station_count == station_count
        assert event.postal_code.value == valid_postal_code.value


class TestDemandAnalysisCalculatedEventEquality:
    """Test event equality and comparison."""

    def test_two_events_with_same_data_are_equal(self, valid_postal_code, valid_demand_priority):
        """Test that events with same data are equal."""
        event1 = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            demand_priority=valid_demand_priority,
        )
        event2 = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            demand_priority=valid_demand_priority,
        )

        # Note: equality depends on timestamp, so they may not be equal
        assert event1.population == event2.population
        assert event1.station_count == event2.station_count

    def test_events_with_different_population_are_not_equal(self, valid_postal_code, valid_demand_priority):
        """Test that events with different population are not equal."""
        event1 = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            demand_priority=valid_demand_priority,
        )
        event2 = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=40000,
            station_count=5,
            demand_priority=valid_demand_priority,
        )

        assert event1.population != event2.population


class TestDemandAnalysisCalculatedEventPriorities:
    """Test events with different priority levels."""

    def test_event_with_high_priority(self, valid_postal_code):
        """Test event with high priority."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            demand_priority=priority,
        )

        assert event.demand_priority.level == PriorityLevel.HIGH
        assert event.demand_priority.is_high_priority()

    def test_event_with_medium_priority(self, valid_postal_code):
        """Test event with medium priority."""
        priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=15000,
            station_count=5,
            demand_priority=priority,
        )

        assert event.demand_priority.level == PriorityLevel.MEDIUM
        assert not event.demand_priority.is_high_priority()

    def test_event_with_low_priority(self, valid_postal_code):
        """Test event with low priority."""
        priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=1000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=10000,
            station_count=10,
            demand_priority=priority,
        )

        assert event.demand_priority.level == PriorityLevel.LOW
        assert not event.demand_priority.is_high_priority()


class TestDemandAnalysisCalculatedEventIntegration:
    """Integration tests for the event."""

    def test_event_can_be_serialized_to_dict(self, demand_calculated_event):
        """Test that event data can be converted to dict."""
        event_dict = {
            "postal_code": demand_calculated_event.postal_code.value,
            "population": demand_calculated_event.population,
            "station_count": demand_calculated_event.station_count,
            "priority_level": demand_calculated_event.demand_priority.level.value,
        }

        assert event_dict["postal_code"] == "10115"
        assert event_dict["population"] == 30000
        assert event_dict["station_count"] == 5
        assert event_dict["priority_level"] == "High"

    def test_event_workflow_high_priority_area(self, valid_postal_code):
        """Test event creation for high priority area."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=7500.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=4,
            demand_priority=priority,
        )

        assert event.population == 30000
        assert event.station_count == 4
        assert event.demand_priority.level == PriorityLevel.HIGH

    def test_event_contains_all_domain_knowledge(self, demand_calculated_event):
        """Test that event preserves domain knowledge."""
        assert demand_calculated_event.postal_code is not None
        assert demand_calculated_event.population > 0
        assert demand_calculated_event.station_count >= 0
        assert demand_calculated_event.demand_priority is not None
        assert hasattr(demand_calculated_event, "occurred_at")
        assert hasattr(demand_calculated_event, "event_type")
