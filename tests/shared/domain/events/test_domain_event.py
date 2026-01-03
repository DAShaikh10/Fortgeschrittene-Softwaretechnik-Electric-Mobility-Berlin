import unittest
from datetime import datetime
from dataclasses import FrozenInstanceError

from src.shared.domain.events.DomainEvent import DomainEvent

class TestDomainEvent(unittest.TestCase):
    """
    Unit tests for the abstract base class DomainEvent.
    """

    def test_default_values(self):
        """
        Test that event_id and occurred_at are generated automatically.
        """
        # We can instantiate DomainEvent directly since it is a dataclass, 
        # even though it is conceptually abstract.
        event = DomainEvent()

        self.assertIsInstance(event.event_id, str)
        self.assertTrue(len(event.event_id) > 0)
        self.assertIsInstance(event.occurred_at, datetime)

    def test_immutability(self):
        """
        Test that DomainEvent attributes cannot be modified (frozen=True).
        """
        event = DomainEvent()
        
        with self.assertRaises(FrozenInstanceError):
            event.event_id = "new-id"

    def test_event_type(self):
        """
        Test that event_type returns the correct class name.
        """
        class MockEvent(DomainEvent):
            pass

        event = MockEvent()
        self.assertEqual(event.event_type(), "MockEvent")

    def test_custom_values(self):
        """
        Test that defaults can be overridden if necessary (via kwargs).
        """
        custom_id = "12345"
        custom_date = datetime(2025, 1, 1)
        
        event = DomainEvent(event_id=custom_id, occurred_at=custom_date)
        
        self.assertEqual(event.event_id, custom_id)
        self.assertEqual(event.occurred_at, custom_date)

if __name__ == '__main__':
    unittest.main()