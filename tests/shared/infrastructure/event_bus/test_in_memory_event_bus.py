"""Tests for In-Memory Event Bus."""
# pylint: disable=redefined-outer-name

from unittest.mock import MagicMock, patch

import pytest

from src.shared.domain.events import DomainEvent
from src.shared.infrastructure.event_bus import InMemoryEventBus

# Renamed to 'SampleEvent' so pytest doesn't try to collect it as a test class
class SampleEvent(DomainEvent):
    """A sample event for testing."""

class AnotherSampleEvent(DomainEvent):
    """Another sample event for testing."""

@pytest.fixture
def event_bus():
    """
    Fixture to provide a fresh instance of InMemoryEventBus for each test.
    """
    return InMemoryEventBus()

def test_initialization(event_bus):
    """
    Test that the event bus initializes with an empty subscriber list.
    """
    # Test behavior instead of internal state
    # An empty event bus should handle publishes without errors
    assert isinstance(event_bus, InMemoryEventBus)
    # Publishing to empty bus should not raise errors
    event_bus.publish(SampleEvent())  # Should complete without errors

def test_subscribe_and_publish(event_bus):
    """
    Test subscribing a handler and publishing an event to it.
    """
    # We must attach a __name__ to the mock because the EventBus logger uses it
    mock_handler = MagicMock()
    mock_handler.__name__ = "test_handler"

    event_bus.subscribe(SampleEvent, mock_handler)

    event = SampleEvent()
    event_bus.publish(event)

    mock_handler.assert_called_once_with(event)

def test_publish_no_subscribers(event_bus):
    """
    Test publishing an event with no subscribers (should not fail).
    """
    event = SampleEvent()
    # Should execute without raising an exception
    event_bus.publish(event)

def test_multiple_subscribers(event_bus):
    """
    Test that multiple handlers for the same event type all get called.
    """
    handler1 = MagicMock()
    handler1.__name__ = "handler1"

    handler2 = MagicMock()
    handler2.__name__ = "handler2"

    event_bus.subscribe(SampleEvent, handler1)
    event_bus.subscribe(SampleEvent, handler2)

    event = SampleEvent()
    event_bus.publish(event)

    handler1.assert_called_once_with(event)
    handler2.assert_called_once_with(event)

def test_different_event_types(event_bus):
    """
    Test that handlers only receive events they subscribed to.
    """
    handler_test = MagicMock()
    handler_test.__name__ = "handler_test"

    handler_another = MagicMock()
    handler_another.__name__ = "handler_another"

    event_bus.subscribe(SampleEvent, handler_test)
    event_bus.subscribe(AnotherSampleEvent, handler_another)

    event1 = SampleEvent()
    event2 = AnotherSampleEvent()

    # Publish first event type
    event_bus.publish(event1)
    handler_test.assert_called_once_with(event1)
    handler_another.assert_not_called()

    # Publish second event type
    event_bus.publish(event2)
    handler_another.assert_called_once_with(event2)

def test_handler_error_isolation(event_bus):
    """
    Test that one handler raising an exception does not prevent other handlers from running.
    """
    failing_handler = MagicMock(side_effect=Exception("Handler crashed"))
    failing_handler.__name__ = "failing_handler"

    working_handler = MagicMock()
    working_handler.__name__ = "working_handler"

    event_bus.subscribe(SampleEvent, failing_handler)
    event_bus.subscribe(SampleEvent, working_handler)

    event = SampleEvent()

    # We expect the error to be logged, but not raised to crash the app
    with patch("src.shared.infrastructure.event_bus.in_memory_event_bus.logger") as mock_logger:
        event_bus.publish(event)

        failing_handler.assert_called_once_with(event)
        working_handler.assert_called_once_with(event)

        # Verify the error was logged
        mock_logger.error.assert_called_once()
        args, _ = mock_logger.error.call_args
        assert "Error handling event" in args[0]

def test_prevent_duplicate_subscription(event_bus):
    """
    Test that subscribing the same handler instance multiple times doesn't add it twice.
    """
    handler = MagicMock()
    handler.__name__ = "handler"

    event_bus.subscribe(SampleEvent, handler)
    event_bus.subscribe(SampleEvent, handler) # Duplicate subscription

    # Test behavior instead of internal state
    # If duplicate prevention works, handler should only be called once
    event = SampleEvent()
    event_bus.publish(event)

    # Handler should still only be called once
    handler.assert_called_once_with(event)
