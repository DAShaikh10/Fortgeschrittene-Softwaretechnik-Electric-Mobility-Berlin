"""
Unit Tests for BaseAggregate.

Test categories:
- Initialization tests
- Event addition tests
- Event retrieval tests
- Event clearing tests
- Event state checking tests
"""

from src.shared.domain.events import DomainEvent
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


class TestBaseAggregateInitialization:
    """Test initialization of BaseAggregate."""

    def test_aggregate_initializes_with_empty_events(self):
        """Test that aggregate starts with no domain events."""
        aggregate = ConcreteAggregate()

        assert aggregate.get_event_count() == 0
        assert aggregate.has_domain_events() is False
        assert not aggregate.get_domain_events()

    def test_multiple_aggregates_have_independent_event_lists(self):
        """Test that multiple aggregates maintain separate event lists."""
        aggregate1 = ConcreteAggregate()
        aggregate2 = ConcreteAggregate()

        event = MockDomainEvent()
        aggregate1.add_event(event)

        assert aggregate1.get_event_count() == 1
        assert aggregate2.get_event_count() == 0


class TestBaseAggregateAddEvent:
    """Test adding domain events to aggregate."""

    def test_add_single_event(self):
        """Test adding a single domain event."""
        aggregate = ConcreteAggregate()
        event = MockDomainEvent()

        aggregate.add_event(event)

        assert aggregate.get_event_count() == 1
        assert aggregate.has_domain_events() is True

    def test_add_multiple_events(self):
        """Test adding multiple domain events."""
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockDomainEvent()
        event3 = MockAnotherDomainEvent()

        aggregate.add_event(event1)
        aggregate.add_event(event2)
        aggregate.add_event(event3)

        assert aggregate.get_event_count() == 3
        assert aggregate.has_domain_events() is True

    def test_events_maintain_order(self):
        """Test that events are maintained in the order they were added."""
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockAnotherDomainEvent()
        event3 = MockDomainEvent()

        aggregate.add_event(event1)
        aggregate.add_event(event2)
        aggregate.add_event(event3)

        events = aggregate.get_domain_events()
        assert events[0] == event1
        assert events[1] == event2
        assert events[2] == event3


class TestBaseAggregateGetEvents:
    """Test retrieving domain events from aggregate."""

    def test_get_domain_events_returns_copy(self):
        """Test that get_domain_events returns a copy, not the original list."""
        aggregate = ConcreteAggregate()
        event = MockDomainEvent()
        aggregate.add_event(event)

        events1 = aggregate.get_domain_events()
        events2 = aggregate.get_domain_events()

        # Should be equal but not the same object
        assert events1 == events2
        assert events1 is not events2

    def test_modifying_returned_events_does_not_affect_aggregate(self):
        """Test that modifying returned event list doesn't affect aggregate."""
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockDomainEvent()

        aggregate.add_event(event1)
        events = aggregate.get_domain_events()
        events.append(event2)  # Modify the returned list

        # Original aggregate should be unchanged
        assert aggregate.get_event_count() == 1
        assert len(events) == 2

    def test_get_domain_events_returns_all_events(self):
        """Test that all added events are returned."""
        aggregate = ConcreteAggregate()
        event1 = MockDomainEvent()
        event2 = MockAnotherDomainEvent()

        aggregate.add_event(event1)
        aggregate.add_event(event2)

        events = aggregate.get_domain_events()
        assert len(events) == 2
        assert event1 in events
        assert event2 in events


class TestBaseAggregateClearEvents:
    """Test clearing domain events from aggregate."""

    def test_clear_domain_events_removes_all_events(self):
        """Test that clear_domain_events removes all events."""
        aggregate = ConcreteAggregate()
        aggregate.add_event(MockDomainEvent())
        aggregate.add_event(MockDomainEvent())
        aggregate.add_event(MockAnotherDomainEvent())

        assert aggregate.get_event_count() == 3

        aggregate.clear_domain_events()

        assert aggregate.get_event_count() == 0
        assert aggregate.has_domain_events() is False
        assert not aggregate.get_domain_events()

    def test_clear_empty_aggregate_does_not_error(self):
        """Test that clearing an aggregate with no events doesn't cause errors."""
        aggregate = ConcreteAggregate()

        aggregate.clear_domain_events()  # Should not raise

        assert aggregate.get_event_count() == 0
        assert aggregate.has_domain_events() is False

    def test_can_add_events_after_clearing(self):
        """Test that events can be added after clearing."""
        aggregate = ConcreteAggregate()
        aggregate.add_event(MockDomainEvent())
        aggregate.clear_domain_events()

        new_event = MockAnotherDomainEvent()
        aggregate.add_event(new_event)

        assert aggregate.get_event_count() == 1
        assert aggregate.has_domain_events() is True


class TestBaseAggregateHasEvents:
    """Test checking if aggregate has domain events."""

    def test_has_domain_events_returns_false_for_empty_aggregate(self):
        """Test has_domain_events returns False when no events exist."""
        aggregate = ConcreteAggregate()

        assert aggregate.has_domain_events() is False

    def test_has_domain_events_returns_true_after_adding_event(self):
        """Test has_domain_events returns True after adding an event."""
        aggregate = ConcreteAggregate()
        aggregate.add_event(MockDomainEvent())

        assert aggregate.has_domain_events() is True

    def test_has_domain_events_returns_false_after_clearing(self):
        """Test has_domain_events returns False after clearing events."""
        aggregate = ConcreteAggregate()
        aggregate.add_event(MockDomainEvent())
        aggregate.clear_domain_events()

        assert aggregate.has_domain_events() is False


class TestBaseAggregateGetEventCount:
    """Test getting the count of domain events."""

    def test_get_event_count_returns_zero_initially(self):
        """Test that event count is zero for new aggregate."""
        aggregate = ConcreteAggregate()

        assert aggregate.get_event_count() == 0

    def test_get_event_count_increments_with_each_event(self):
        """Test that event count increments as events are added."""
        aggregate = ConcreteAggregate()

        assert aggregate.get_event_count() == 0

        aggregate.add_event(MockDomainEvent())
        assert aggregate.get_event_count() == 1

        aggregate.add_event(MockDomainEvent())
        assert aggregate.get_event_count() == 2

        aggregate.add_event(MockAnotherDomainEvent())
        assert aggregate.get_event_count() == 3

    def test_get_event_count_returns_zero_after_clearing(self):
        """Test that event count is zero after clearing."""
        aggregate = ConcreteAggregate()
        aggregate.add_event(MockDomainEvent())
        aggregate.add_event(MockDomainEvent())

        aggregate.clear_domain_events()

        assert aggregate.get_event_count() == 0


class TestBaseAggregateIntegration:
    """Integration tests for complete event workflow."""

    def test_typical_aggregate_lifecycle(self):
        """Test a typical lifecycle: add events, get them, clear them."""
        aggregate = ConcreteAggregate()

        # Start empty
        assert aggregate.get_event_count() == 0
        assert not aggregate.has_domain_events()

        # Add events
        event1 = MockDomainEvent()
        event2 = MockAnotherDomainEvent()
        aggregate.add_event(event1)
        aggregate.add_event(event2)

        # Verify state
        assert aggregate.get_event_count() == 2
        assert aggregate.has_domain_events()

        # Get and verify events
        events = aggregate.get_domain_events()
        assert len(events) == 2
        assert event1 in events
        assert event2 in events

        # Clear events (simulate publishing)
        aggregate.clear_domain_events()
        assert aggregate.get_event_count() == 0
        assert not aggregate.has_domain_events()

        # Add new events after clearing
        event3 = MockDomainEvent()
        aggregate.add_event(event3)
        assert aggregate.get_event_count() == 1

    def test_multiple_get_clear_cycles(self):
        """Test multiple cycles of adding, getting, and clearing events."""
        aggregate = ConcreteAggregate()

        # Cycle 1
        aggregate.add_event(MockDomainEvent())
        assert aggregate.get_event_count() == 1
        aggregate.clear_domain_events()
        assert aggregate.get_event_count() == 0

        # Cycle 2
        aggregate.add_event(MockDomainEvent())
        aggregate.add_event(MockAnotherDomainEvent())
        assert aggregate.get_event_count() == 2
        aggregate.clear_domain_events()
        assert aggregate.get_event_count() == 0

        # Cycle 3
        aggregate.add_event(MockAnotherDomainEvent())
        assert aggregate.get_event_count() == 1
        events = aggregate.get_domain_events()
        assert len(events) == 1
        assert isinstance(events[0], MockAnotherDomainEvent)
