"""Tests for High Demand Area Identified Event."""
# pylint: disable=redefined-outer-name

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from src.demand.domain.events import HighDemandAreaIdentifiedEvent
from src.shared.domain.value_objects import PostalCode


@pytest.fixture
def valid_postal_code():
    """Create a valid postal code."""
    return PostalCode("10115")


@pytest.fixture
def high_demand_event(valid_postal_code):
    """Create a high demand area identified event."""
    return HighDemandAreaIdentifiedEvent(
        postal_code=valid_postal_code,
        population=30000,
        station_count=5,
        urgency_score=75.0,
    )


class TestHighDemandAreaIdentifiedEventInitialization:
    """Test event initialization."""

    def test_event_initialization_with_valid_data(self, valid_postal_code):
        """Test creating event with valid data."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )

        assert event.postal_code == valid_postal_code
        assert event.population == 30000
        assert event.station_count == 5
        assert event.urgency_score == 75.0

    def test_event_initialization_with_zero_population(self, valid_postal_code):
        """Test event with zero population."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=0,
            station_count=5,
            urgency_score=50.0,
        )

        assert event.population == 0

    def test_event_initialization_with_zero_stations(self, valid_postal_code):
        """Test event with zero stations."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=50000,
            station_count=0,
            urgency_score=100.0,
        )

        assert event.station_count == 0

    def test_event_initialization_with_critical_urgency(self, valid_postal_code):
        """Test event with critical urgency score."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=100000,
            station_count=2,
            urgency_score=100.0,
        )

        assert event.urgency_score == 100.0

    def test_event_initialization_with_minimum_urgency(self, valid_postal_code):
        """Test event with minimum urgency score (still high priority)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )

        assert event.urgency_score == 75.0

    def test_event_initialization_with_large_numbers(self, valid_postal_code):
        """Test event with large population and station counts."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=1000000,
            station_count=500,
            urgency_score=95.0,
        )

        assert event.population == 1000000
        assert event.station_count == 500


class TestHighDemandAreaIdentifiedEventImmutability:
    """Test immutability of frozen dataclass."""

    def test_cannot_modify_postal_code(self, high_demand_event):
        """Test that postal code cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            high_demand_event.postal_code = PostalCode("12345")

    def test_cannot_modify_population(self, high_demand_event):
        """Test that population cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            high_demand_event.population = 50000

    def test_cannot_modify_station_count(self, high_demand_event):
        """Test that station count cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            high_demand_event.station_count = 10

    def test_cannot_modify_urgency_score(self, high_demand_event):
        """Test that urgency score cannot be modified."""
        with pytest.raises(FrozenInstanceError):
            high_demand_event.urgency_score = 50.0


class TestHighDemandAreaIdentifiedEventType:
    """Test event type information."""

    def test_event_has_type_attribute(self, high_demand_event):
        """Test that event has a type attribute."""
        assert hasattr(high_demand_event, "event_type")
        assert high_demand_event.event_type is not None

    def test_event_type_name_matches_class(self, high_demand_event):
        """Test that event type name matches class name."""
        assert "HighDemandAreaIdentifiedEvent" in str(high_demand_event.event_type)

    def test_multiple_events_have_same_class_type(self, valid_postal_code):
        """Test that multiple events have the same class type."""
        event1 = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )
        event2 = HighDemandAreaIdentifiedEvent(
            postal_code=PostalCode("12345"),
            population=20000,
            station_count=4,
            urgency_score=100.0,
        )

        assert type(event1) == type(event2)
        assert type(event1).__name__ == "HighDemandAreaIdentifiedEvent"


class TestHighDemandAreaIdentifiedEventData:
    """Test event data and attributes."""

    def test_event_contains_all_required_fields(self, high_demand_event):
        """Test that event has all required fields."""
        assert hasattr(high_demand_event, "postal_code")
        assert hasattr(high_demand_event, "population")
        assert hasattr(high_demand_event, "station_count")
        assert hasattr(high_demand_event, "urgency_score")

    def test_event_has_timestamp(self, high_demand_event):
        """Test that event has a timestamp from DomainEvent."""
        assert hasattr(high_demand_event, "occurred_at")
        assert high_demand_event.occurred_at is not None

    def test_event_timestamp_is_datetime(self, high_demand_event):
        """Test that timestamp is a datetime object."""
        assert isinstance(high_demand_event.occurred_at, datetime)

    def test_event_data_preservation(self, valid_postal_code):
        """Test that event data is preserved correctly."""
        population = 25000
        station_count = 3
        urgency_score = 85.5
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=population,
            station_count=station_count,
            urgency_score=urgency_score,
        )

        assert event.population == population
        assert event.station_count == station_count
        assert event.urgency_score == urgency_score
        assert event.postal_code.value == valid_postal_code.value


class TestHighDemandAreaIdentifiedEventEquality:
    """Test event equality and comparison."""

    def test_two_events_with_same_data(self, valid_postal_code):
        """Test events with same data (note: timestamps will differ)."""
        event1 = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )
        event2 = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )

        assert event1.population == event2.population
        assert event1.station_count == event2.station_count
        assert event1.urgency_score == event2.urgency_score

    def test_events_with_different_urgency_scores(self, valid_postal_code):
        """Test that events with different urgency scores are different."""
        event1 = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )
        event2 = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=100.0,
        )

        assert event1.urgency_score != event2.urgency_score


class TestHighDemandAreaIdentifiedEventUrgencyScores:
    """Test events with different urgency score levels."""

    def test_event_with_critical_urgency_100(self, valid_postal_code):
        """Test event with critical urgency (100.0)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=50000,
            station_count=4,
            urgency_score=100.0,
        )

        assert event.urgency_score == 100.0

    def test_event_with_high_urgency_75(self, valid_postal_code):
        """Test event with high urgency (75.0)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )

        assert event.urgency_score == 75.0

    def test_event_with_medium_urgency_50(self, valid_postal_code):
        """Test event with medium urgency (50.0)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=20000,
            station_count=8,
            urgency_score=50.0,
        )

        assert event.urgency_score == 50.0

    def test_event_with_low_urgency_25(self, valid_postal_code):
        """Test event with low urgency (25.0)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=10000,
            station_count=10,
            urgency_score=25.0,
        )

        assert event.urgency_score == 25.0

    def test_urgency_score_comparison(self, valid_postal_code):
        """Test urgency score comparison between events."""
        critical = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=50000,
            station_count=2,
            urgency_score=100.0,
        )
        high = HighDemandAreaIdentifiedEvent(
            postal_code=PostalCode("12345"),
            population=30000,
            station_count=5,
            urgency_score=75.0,
        )

        assert critical.urgency_score > high.urgency_score
        assert critical.urgency_score == 100.0


class TestHighDemandAreaIdentifiedEventIntegration:
    """Integration tests for the event."""

    def test_event_can_be_serialized_to_dict(self, high_demand_event):
        """Test that event data can be converted to dict."""
        event_dict = {
            "postal_code": high_demand_event.postal_code.value,
            "population": high_demand_event.population,
            "station_count": high_demand_event.station_count,
            "urgency_score": high_demand_event.urgency_score,
        }

        assert event_dict["postal_code"] == "10115"
        assert event_dict["population"] == 30000
        assert event_dict["station_count"] == 5
        assert event_dict["urgency_score"] == 75.0

    def test_event_workflow_critical_shortage(self, valid_postal_code):
        """Test event creation for area with critical shortage."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=100000,
            station_count=2,
            urgency_score=100.0,
        )

        assert event.population == 100000
        assert event.station_count == 2
        assert event.urgency_score == 100.0

    def test_event_workflow_high_demand(self, valid_postal_code):
        """Test event creation for high demand area."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=4,
            urgency_score=75.0,
        )

        assert event.population == 30000
        assert event.station_count == 4
        assert event.urgency_score == 75.0

    def test_event_contains_all_domain_knowledge(self, high_demand_event):
        """Test that event preserves domain knowledge."""
        assert high_demand_event.postal_code is not None
        assert high_demand_event.population > 0
        assert high_demand_event.station_count >= 0
        assert 0.0 <= high_demand_event.urgency_score <= 100.0
        assert hasattr(high_demand_event, "occurred_at")
        assert hasattr(high_demand_event, "event_type")

    def test_event_represents_integration_concern(self, valid_postal_code):
        """Test that event captures integration event characteristics."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=40000,
            station_count=6,
            urgency_score=80.0,
        )

        # Verify it has the characteristics of an integration event
        assert event.postal_code is not None  # Domain identity
        assert event.urgency_score >= 75.0  # Only high priority areas
        assert event.occurred_at is not None  # Temporal information
        assert event.event_id is not None  # Unique identity


class TestHighDemandAreaIdentifiedEventBoundaryConditions:
    """Test boundary conditions and edge cases."""

    def test_maximum_population(self, valid_postal_code):
        """Test event with very large population."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=10000000,
            station_count=100,
            urgency_score=95.0,
        )

        assert event.population == 10000000

    def test_minimum_nonzero_population(self, valid_postal_code):
        """Test event with minimal population."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=1,
            station_count=1,
            urgency_score=1.0,
        )

        assert event.population == 1

    def test_urgency_score_precision(self, valid_postal_code):
        """Test event with precise urgency score."""
        urgency = 87.5
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=5,
            urgency_score=urgency,
        )

        assert event.urgency_score == urgency

    def test_fractional_urgency_scores(self, valid_postal_code):
        """Test various fractional urgency scores."""
        scores = [25.5, 50.25, 75.75, 99.99]

        for score in scores:
            event = HighDemandAreaIdentifiedEvent(
                postal_code=valid_postal_code,
                population=30000,
                station_count=5,
                urgency_score=score,
            )
            assert event.urgency_score == score
