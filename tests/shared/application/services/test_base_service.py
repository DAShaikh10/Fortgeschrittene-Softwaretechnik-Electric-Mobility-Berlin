"""
Unit Tests for BaseService.

Test categories:
- Initialization tests
- Event publishing tests
- Event bus interaction tests
- Aggregate event handling tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import Mock, call

import pytest

from src.shared.application.services import BaseService
from src.shared.domain.events import DomainEvent, IDomainEventPublisher
from src.shared.domain.aggregates import BaseAggregate


# Test fixtures and helper classes
class MockDomainEvent(DomainEvent):
    """Mock event class for unit testing."""


class MockAnotherDomainEvent(DomainEvent):
    """Another mock event class for unit testing."""


class ConcreteAggregate(BaseAggregate):
    """Concrete test aggregate inheriting from BaseAggregate."""

    def add_event(self, event: DomainEvent):
        """Public method to add events for testing."""
        self._add_domain_event(event)


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock()


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus implementing IDomainEventPublisher."""
    event_bus = Mock(spec=IDomainEventPublisher)
    return event_bus


@pytest.fixture
def base_service_with_event_bus(mock_repository, mock_event_bus):
    """Create a BaseService instance with event bus."""
    return BaseService(mock_repository, mock_event_bus)


@pytest.fixture
def base_service_without_event_bus(mock_repository):
    """Create a BaseService instance without event bus."""
    return BaseService(mock_repository)


@pytest.fixture
def aggregate_with_events():
    """Create an aggregate with multiple events."""
    aggregate = ConcreteAggregate()
    event1 = MockDomainEvent()
    event2 = MockAnotherDomainEvent()
    aggregate.add_event(event1)
    aggregate.add_event(event2)
    return aggregate


class TestBaseServiceInitialization:
    """Test initialization of BaseService."""

    def test_service_initializes_with_repository_and_event_bus(self, mock_repository, mock_event_bus):
        """Test that service initializes with both repository and event bus."""
        service = BaseService(mock_repository, mock_event_bus)

        assert service.repository is mock_repository
        assert service.event_bus is mock_event_bus

    def test_service_initializes_with_repository_only(self, mock_repository):
        """Test that service initializes with repository and no event bus."""
        service = BaseService(mock_repository)

        assert service.repository is mock_repository
        assert service.event_bus is None

    def test_service_initializes_with_none_event_bus_explicitly(self, mock_repository):
        """Test that service can be initialized with None event bus explicitly."""
        service = BaseService(mock_repository, None)

        assert service.repository is mock_repository
        assert service.event_bus is None


class TestBaseServicePublishEvents:
    """Test event publishing functionality."""

    def test_publish_events_publishes_all_events_to_event_bus(
        self, base_service_with_event_bus, aggregate_with_events, mock_event_bus
    ):
        """Test that publish_events publishes all events from aggregate to event bus."""
        base_service_with_event_bus.publish_events(aggregate_with_events)

        assert mock_event_bus.publish.call_count == 2
        published_events = [call_args[0][0] for call_args in mock_event_bus.publish.call_args_list]
        assert isinstance(published_events[0], MockDomainEvent)
        assert isinstance(published_events[1], MockAnotherDomainEvent)

    def test_publish_events_clears_aggregate_events_after_publishing(
        self, base_service_with_event_bus, aggregate_with_events
    ):
        """Test that publish_events clears events from aggregate after publishing."""
        assert aggregate_with_events.has_domain_events() is True

        base_service_with_event_bus.publish_events(aggregate_with_events)

        assert aggregate_with_events.has_domain_events() is False
        assert aggregate_with_events.get_event_count() == 0

    def test_publish_events_with_empty_aggregate_does_not_publish(self, base_service_with_event_bus, mock_event_bus):
        """Test that publish_events handles aggregate with no events gracefully."""
        empty_aggregate = ConcreteAggregate()

        base_service_with_event_bus.publish_events(empty_aggregate)

        mock_event_bus.publish.assert_not_called()
        assert empty_aggregate.has_domain_events() is False

    def test_publish_events_without_event_bus_does_nothing(self, base_service_without_event_bus):
        """Test that publish_events returns early when no event bus configured."""
        aggregate = ConcreteAggregate()
        event = MockDomainEvent()
        aggregate.add_event(event)

        # Should not raise error
        base_service_without_event_bus.publish_events(aggregate)

        # Events should NOT be cleared when no event bus
        assert aggregate.has_domain_events() is True
        assert aggregate.get_event_count() == 1

    def test_publish_events_publishes_events_in_order(self, base_service_with_event_bus, mock_event_bus):
        """Test that events are published in the order they were added."""
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockAnotherDomainEvent()
        event3 = MockDomainEvent()

        aggregate.add_event(event1)
        aggregate.add_event(event2)
        aggregate.add_event(event3)

        base_service_with_event_bus.publish_events(aggregate)

        assert mock_event_bus.publish.call_count == 3
        calls = mock_event_bus.publish.call_args_list
        assert calls[0] == call(event1)
        assert calls[1] == call(event2)
        assert calls[2] == call(event3)


class TestBaseServiceEventBusInteraction:
    """Test interaction with event bus."""

    def test_service_calls_event_bus_publish_for_each_event(self, base_service_with_event_bus, mock_event_bus):
        """Test that service calls event bus publish method for each event."""
        aggregate = ConcreteAggregate()
        events = [MockDomainEvent(), MockAnotherDomainEvent(), MockDomainEvent()]

        for event in events:
            aggregate.add_event(event)

        base_service_with_event_bus.publish_events(aggregate)

        assert mock_event_bus.publish.call_count == len(events)

    def test_service_handles_event_bus_with_no_publish_side_effects(self, base_service_with_event_bus, mock_event_bus):
        """Test that service works correctly even if event bus publish has no side effects."""
        aggregate = ConcreteAggregate()
        aggregate.add_event(MockDomainEvent())

        # Event bus publish should be called but does nothing
        mock_event_bus.publish.return_value = None

        base_service_with_event_bus.publish_events(aggregate)

        mock_event_bus.publish.assert_called_once()
        assert aggregate.has_domain_events() is False


class TestBaseServiceAggregateEventHandling:
    """Test handling of aggregate domain events."""

    def test_publish_events_with_single_event(self, base_service_with_event_bus, mock_event_bus):
        """Test publishing with single event in aggregate."""
        aggregate = ConcreteAggregate()
        event = MockDomainEvent()
        aggregate.add_event(event)

        base_service_with_event_bus.publish_events(aggregate)

        mock_event_bus.publish.assert_called_once_with(event)
        assert aggregate.get_event_count() == 0

    def test_publish_events_with_multiple_identical_events(self, base_service_with_event_bus, mock_event_bus):
        """Test publishing multiple events of the same type."""
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockDomainEvent()
        event3 = MockDomainEvent()

        aggregate.add_event(event1)
        aggregate.add_event(event2)
        aggregate.add_event(event3)

        base_service_with_event_bus.publish_events(aggregate)

        assert mock_event_bus.publish.call_count == 3
        assert aggregate.has_domain_events() is False

    def test_aggregate_events_cleared_only_after_all_published(
        self, base_service_with_event_bus, mock_event_bus, aggregate_with_events
    ):
        """Test that aggregate events are cleared after all events are published."""
        initial_event_count = aggregate_with_events.get_event_count()
        assert initial_event_count > 0

        base_service_with_event_bus.publish_events(aggregate_with_events)

        # All events should have been published
        assert mock_event_bus.publish.call_count == initial_event_count
        # Aggregate should be cleared
        assert aggregate_with_events.get_event_count() == 0


class TestBaseServiceIntegration:
    """Integration tests combining multiple features."""

    def test_full_workflow_with_event_bus(self, mock_repository, mock_event_bus):
        """Test complete workflow: initialize service, add events, publish."""
        # Initialize service
        service = BaseService(mock_repository, mock_event_bus)

        # Create aggregate with events
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockAnotherDomainEvent()
        aggregate.add_event(event1)
        aggregate.add_event(event2)

        # Publish events
        service.publish_events(aggregate)

        # Verify all events published
        assert mock_event_bus.publish.call_count == 2
        # Verify aggregate cleared
        assert aggregate.has_domain_events() is False

    def test_full_workflow_without_event_bus(self, mock_repository):
        """Test complete workflow without event bus configured."""
        # Initialize service without event bus
        service = BaseService(mock_repository, None)

        # Create aggregate with events
        aggregate = ConcreteAggregate()
        event = MockDomainEvent()
        aggregate.add_event(event)

        # Publish events (should be no-op)
        service.publish_events(aggregate)

        # Events should remain because no event bus
        assert aggregate.has_domain_events() is True

    def test_multiple_publish_cycles(self, base_service_with_event_bus, mock_event_bus):
        """Test multiple cycles of adding and publishing events."""
        aggregate = ConcreteAggregate()

        # First cycle
        aggregate.add_event(MockDomainEvent())
        base_service_with_event_bus.publish_events(aggregate)
        assert aggregate.get_event_count() == 0
        assert mock_event_bus.publish.call_count == 1

        # Second cycle
        aggregate.add_event(MockAnotherDomainEvent())
        aggregate.add_event(MockDomainEvent())
        base_service_with_event_bus.publish_events(aggregate)
        assert aggregate.get_event_count() == 0
        assert mock_event_bus.publish.call_count == 3

        # Third cycle with no events
        base_service_with_event_bus.publish_events(aggregate)
        assert aggregate.get_event_count() == 0
        assert mock_event_bus.publish.call_count == 3  # No new calls

    def test_service_with_different_aggregate_instances(self, base_service_with_event_bus, mock_event_bus):
        """Test service can handle events from different aggregate instances."""
        aggregate1 = ConcreteAggregate()
        aggregate1.add_event(MockDomainEvent())

        aggregate2 = ConcreteAggregate()
        aggregate2.add_event(MockAnotherDomainEvent())

        base_service_with_event_bus.publish_events(aggregate1)
        base_service_with_event_bus.publish_events(aggregate2)

        assert mock_event_bus.publish.call_count == 2
        assert aggregate1.get_event_count() == 0
        assert aggregate2.get_event_count() == 0
