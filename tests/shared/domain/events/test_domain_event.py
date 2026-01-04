"""
Shared Domain Tests.
"""

from dataclasses import FrozenInstanceError
from datetime import datetime
import pytest

from src.shared.domain.events.DomainEvent import DomainEvent


def test_default_values():
    """
    Test that event_id and occurred_at are generated automatically.
    """
    event = DomainEvent()

    assert isinstance(event.event_id, str)
    assert len(event.event_id) > 0
    assert isinstance(event.occurred_at, datetime)


def test_immutability():
    """
    Test that DomainEvent attributes cannot be modified (frozen=True).
    """
    event = DomainEvent()

    with pytest.raises(FrozenInstanceError):
        event.event_id = "new-id"


def test_event_type():
    """
    Test that event_type returns the correct class name.
    """

    class MockEvent(DomainEvent):
        """Simple domain event for testing type resolution."""

    event = MockEvent()
    assert event.event_type() == "MockEvent"


def test_custom_values():
    """
    Test that defaults can be overridden if necessary (via kwargs).
    """
    custom_id = "12345"
    custom_date = datetime(2025, 1, 1)

    event = DomainEvent(event_id=custom_id, occurred_at=custom_date)

    assert event.event_id == custom_id
    assert event.occurred_at == custom_date
