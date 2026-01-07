"""Tests for Stations Found Event."""

# pylint: disable=redefined-outer-name

from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock
import pytest

from src.shared.domain.events import StationsFoundEvent
from src.shared.domain.value_objects import PostalCode


@pytest.fixture
def mock_postal_code():
    """
    Pytest fixture to provide a mock PostalCode.
    """
    mock = MagicMock(spec=PostalCode)
    mock.value = "10115"
    return mock


def test_initialization(mock_postal_code):
    """
    Test that the event is initialized correctly with required fields.
    """
    stations_found = 5

    event = StationsFoundEvent(postal_code=mock_postal_code, stations_found=stations_found)

    assert event.postal_code == mock_postal_code
    assert event.stations_found == stations_found
    assert event.event_id is not None
    assert event.occurred_at is not None


def test_immutability(mock_postal_code):
    """
    Test that attributes cannot be changed after creation.
    """
    event = StationsFoundEvent(postal_code=mock_postal_code, stations_found=3)

    with pytest.raises(FrozenInstanceError):
        event.postal_code = MagicMock()

    with pytest.raises(FrozenInstanceError):
        event.stations_found = 10


def test_event_type_name(mock_postal_code):
    """
    Test that the event type name is correct.
    """
    event = StationsFoundEvent(postal_code=mock_postal_code, stations_found=2)

    assert event.event_type() == "StationsFoundEvent"


def test_different_instances_have_unique_ids(mock_postal_code):
    """
    Test that each event instance gets a unique event_id.
    """
    event1 = StationsFoundEvent(postal_code=mock_postal_code, stations_found=1)
    event2 = StationsFoundEvent(postal_code=mock_postal_code, stations_found=1)

    assert event1.event_id != event2.event_id


def test_stations_found_count_variations(mock_postal_code):
    """
    Test that different station counts are captured correctly.
    """
    counts = [1, 3, 10, 25, 100]

    for count in counts:
        event = StationsFoundEvent(postal_code=mock_postal_code, stations_found=count)
        assert event.stations_found == count
