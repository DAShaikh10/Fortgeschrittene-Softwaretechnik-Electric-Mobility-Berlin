import unittest
from src.shared.domain.events.IDomainEventPublisher import IDomainEventPublisher
from src.shared.domain.events.DomainEvent import DomainEvent

class TestIDomainEventPublisher(unittest.TestCase):
    """
    Unit tests for the IDomainEventPublisher interface contract.
    """

    def test_cannot_instantiate_interface(self):
        """
        Test that the interface cannot be instantiated directly because of abstract methods.
        """
        # Attempting to instantiate an abstract class with abstract methods raises TypeError
        with self.assertRaises(TypeError):
            IDomainEventPublisher()

    def test_concrete_implementation(self):
        """
        Test that a concrete class implementing all methods works correctly.
        """
        class ConcretePublisher(IDomainEventPublisher):
            def subscribe(self, event_type, handler):
                pass
            def publish(self, event):
                pass
        
        publisher = ConcretePublisher()
        self.assertIsInstance(publisher, IDomainEventPublisher)

    def test_incomplete_implementation(self):
        """
        Test that a concrete class failing to implement methods raises error.
        """
        class IncompletePublisher(IDomainEventPublisher):
            def publish(self, event):
                pass
            # Missing subscribe method
        
        with self.assertRaises(TypeError):
            IncompletePublisher()

if __name__ == '__main__':
    unittest.main()