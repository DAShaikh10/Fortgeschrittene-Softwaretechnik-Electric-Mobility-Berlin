"""Tests for Station Search Performed Event."""
# pylint: disable=redefined-outer-name

from dataclasses import FrozenInstanceError
from unittest.mock import MagicMock
import pytest

from src.shared.domain.events import StationSearchPerformedEvent
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
    stations_count = 10

    event = StationSearchPerformedEvent(
        postal_code=mock_postal_code,
        stations_found=stations_count
    )

    assert event.postal_code == mock_postal_code
    assert event.stations_found == stations_count
    assert event.search_parameters == {} # Default empty dict

    # Verify inherited fields
    assert event.event_id is not None
    assert event.occurred_at is not None

def test_initialization_with_parameters(mock_postal_code):
    """
    Test initialization with optional search_parameters.
    """
    params = {"origin": mock_postal_code}

    event = StationSearchPerformedEvent(
        postal_code=mock_postal_code,
        stations_found=5,
        search_parameters=params
    )

    assert event.search_parameters == params

def test_immutability(mock_postal_code):
    """
    Test that attributes cannot be changed after creation.
    """
    event = StationSearchPerformedEvent(
        postal_code=mock_postal_code,
        stations_found=5
    )

    with pytest.raises(FrozenInstanceError):
        event.stations_found = 0

def test_event_type_name(mock_postal_code):
    """
    Test that the event type name is correct.
    """
    event = StationSearchPerformedEvent(
        postal_code=mock_postal_code,
        stations_found=5
    )
    assert event.event_type() == "StationSearchPerformedEvent"
