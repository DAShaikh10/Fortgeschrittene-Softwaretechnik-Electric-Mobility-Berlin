"""Tests for IDomainEventPublisher."""

# pylint: disable=abstract-class-instantiated

import pytest
from src.shared.domain.events import IDomainEventPublisher


def test_cannot_instantiate_interface():
    """
    Test that the interface cannot be instantiated directly because of abstract methods.
    """
    with pytest.raises(TypeError):
        IDomainEventPublisher()


def test_concrete_implementation():
    """
    Test that a concrete class implementing all methods works correctly.
    """

    class ConcretePublisher(IDomainEventPublisher):
        """Concrete implementation of IDomainEventPublisher for testing."""

        def subscribe(self, event_type, handler):
            pass

        def publish(self, event):
            pass

    publisher = ConcretePublisher()
    assert isinstance(publisher, IDomainEventPublisher)


def test_incomplete_implementation():
    """
    Test that a concrete class failing to implement methods raises error.
    """

    class IncompletePublisher(IDomainEventPublisher):
        """Incomplete implementation missing subscribe method."""

        def publish(self, event):
            pass

        # Missing subscribe method

    with pytest.raises(TypeError):
        IncompletePublisher()
