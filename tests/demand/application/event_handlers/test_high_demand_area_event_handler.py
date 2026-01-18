"""
Unit Tests for HighDemandAreaEventHandler.

Test categories:
- Event handling tests
- Logging validation tests
- Edge cases and data variations
"""

# pylint: disable=redefined-outer-name

from unittest.mock import patch

import pytest

from src.demand.application.event_handlers import HighDemandAreaEventHandler
from src.demand.domain.events import HighDemandAreaIdentifiedEvent
from src.shared.domain.value_objects import PostalCode


# Test fixtures
@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def high_urgency_event(valid_postal_code):
    """Create a high demand area event with high urgency score."""
    return HighDemandAreaIdentifiedEvent(
        postal_code=valid_postal_code,
        population=50000,
        station_count=5,
        urgency_score=100.0,
    )


@pytest.fixture
def medium_urgency_event(valid_postal_code):
    """Create a high demand area event with medium urgency score."""
    return HighDemandAreaIdentifiedEvent(
        postal_code=valid_postal_code,
        population=20000,
        station_count=4,
        urgency_score=75.0,
    )


@pytest.fixture
def low_urgency_event(valid_postal_code):
    """Create a high demand area event with low urgency score."""
    return HighDemandAreaIdentifiedEvent(
        postal_code=valid_postal_code,
        population=12000,
        station_count=6,
        urgency_score=50.0,
    )


class TestHighDemandAreaEventHandlerBasicFunctionality:
    """Test basic event handler functionality."""

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_high_urgency_event_with_correct_format(self, mock_logger, high_urgency_event):
        """Test that handle method logs high urgency events with proper formatting."""
        HighDemandAreaEventHandler.handle(high_urgency_event)

        mock_logger.warning.assert_called_once_with(
            "[EVENT] HIGH DEMAND AREA IDENTIFIED: Postal Code %s | Urgency Score: %.2f | Population: %d | Stations: %d",
            "10115",
            100.0,
            50000,
            5,
        )

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_medium_urgency_event(self, mock_logger, medium_urgency_event):
        """Test that handle method logs medium urgency events correctly."""
        HighDemandAreaEventHandler.handle(medium_urgency_event)

        mock_logger.warning.assert_called_once_with(
            "[EVENT] HIGH DEMAND AREA IDENTIFIED: Postal Code %s | Urgency Score: %.2f | Population: %d | Stations: %d",
            "10115",
            75.0,
            20000,
            4,
        )

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_low_urgency_event(self, mock_logger, low_urgency_event):
        """Test that handle method logs low urgency events correctly."""
        HighDemandAreaEventHandler.handle(low_urgency_event)

        mock_logger.warning.assert_called_once_with(
            "[EVENT] HIGH DEMAND AREA IDENTIFIED: Postal Code %s | Urgency Score: %.2f | Population: %d | Stations: %d",
            "10115",
            50.0,
            12000,
            6,
        )

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_returns_none(self, high_urgency_event):
        """Test that handle method returns None."""
        assert HighDemandAreaEventHandler.handle(high_urgency_event) is None

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_is_static_method(self, mock_logger, high_urgency_event):
        """Test that handle can be called as a static method without instantiation."""
        # Call without creating an instance
        HighDemandAreaEventHandler.handle(high_urgency_event)

        # Verify it was called
        assert mock_logger.warning.call_count == 1


class TestHighDemandAreaEventHandlerWithVariousPostalCodes:
    """Test event handler with different postal codes."""

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_different_postal_code_10xxx(self, mock_logger):
        """Test logging with postal code starting with 10."""
        postal_code = PostalCode("10178")
        event = HighDemandAreaIdentifiedEvent(
            postal_code=postal_code,
            population=35000,
            station_count=3,
            urgency_score=90.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[1] == "10178"

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_postal_code_12xxx(self, mock_logger):
        """Test logging with postal code starting with 12."""
        postal_code = PostalCode("12345")
        event = HighDemandAreaIdentifiedEvent(
            postal_code=postal_code,
            population=28000,
            station_count=5,
            urgency_score=85.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[1] == "12345"

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_postal_code_13xxx(self, mock_logger):
        """Test logging with postal code starting with 13."""
        postal_code = PostalCode("13579")
        event = HighDemandAreaIdentifiedEvent(
            postal_code=postal_code,
            population=18000,
            station_count=3,
            urgency_score=70.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[1] == "13579"

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_postal_code_14xxx(self, mock_logger):
        """Test logging with postal code starting with 14."""
        postal_code = PostalCode("14195")
        event = HighDemandAreaIdentifiedEvent(
            postal_code=postal_code,
            population=42000,
            station_count=2,
            urgency_score=95.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[1] == "14195"


class TestHighDemandAreaEventHandlerEdgeCases:
    """Test event handler with edge cases and boundary values."""

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_zero_stations(self, mock_logger, valid_postal_code):
        """Test logging when station count is zero (critical shortage)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=80000,
            station_count=0,
            urgency_score=100.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once_with(
            "[EVENT] HIGH DEMAND AREA IDENTIFIED: Postal Code %s | Urgency Score: %.2f | Population: %d | Stations: %d",
            "10115",
            100.0,
            80000,
            0,
        )

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_single_station(self, mock_logger, valid_postal_code):
        """Test logging when there is exactly one station."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=30000,
            station_count=1,
            urgency_score=98.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[4] == 1  # station_count

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_large_population(self, mock_logger, valid_postal_code):
        """Test logging with very large population."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=1500000,
            station_count=50,
            urgency_score=100.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[3] == 1500000  # population

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_many_stations(self, mock_logger, valid_postal_code):
        """Test logging with large number of stations but still high demand."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=100000,
            station_count=100,
            urgency_score=60.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[4] == 100  # station_count

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_fractional_urgency_score(self, mock_logger, valid_postal_code):
        """Test that urgency score is logged with two decimal places."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=25000,
            station_count=5,
            urgency_score=87.6543,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        # Check the format string uses %.2f
        format_string = mock_logger.warning.call_args[0][0]
        assert "%.2f" in format_string
        # Check the actual value
        args = mock_logger.warning.call_args[0]
        assert args[2] == 87.6543

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_maximum_urgency_score(self, mock_logger, valid_postal_code):
        """Test logging with maximum urgency score (100.0)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=50000,
            station_count=1,
            urgency_score=100.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[2] == 100.0

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_minimum_high_urgency_score(self, mock_logger, valid_postal_code):
        """Test logging with minimum urgency score for high demand (50.0)."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=15000,
            station_count=7,
            urgency_score=50.0,
        )

        HighDemandAreaEventHandler.handle(event)

        mock_logger.warning.assert_called_once()
        args = mock_logger.warning.call_args[0]
        assert args[2] == 50.0

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_event_with_decimal_urgency_score(self, mock_logger, valid_postal_code):
        """Test logging with typical decimal urgency scores."""
        urgency_scores = [75.5, 82.33, 91.99, 67.25]

        for score in urgency_scores:
            event = HighDemandAreaIdentifiedEvent(
                postal_code=valid_postal_code,
                population=20000,
                station_count=3,
                urgency_score=score,
            )
            HighDemandAreaEventHandler.handle(event)

        assert mock_logger.warning.call_count == 4


class TestHighDemandAreaEventHandlerLoggerIntegration:
    """Test integration with the logging system."""

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_calls_logger_warning_not_info_or_error(self, mock_logger, high_urgency_event):
        """Test that handler uses warning level logging, not info or error."""
        HighDemandAreaEventHandler.handle(high_urgency_event)

        mock_logger.warning.assert_called_once()
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()
        mock_logger.debug.assert_not_called()

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_with_event_prefix(self, mock_logger, high_urgency_event):
        """Test that log message includes [EVENT] prefix."""
        HighDemandAreaEventHandler.handle(high_urgency_event)

        format_string = mock_logger.warning.call_args[0][0]
        assert format_string.startswith("[EVENT]")

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_logs_with_high_demand_identifier(self, mock_logger, high_urgency_event):
        """Test that log message includes HIGH DEMAND AREA IDENTIFIED text."""
        HighDemandAreaEventHandler.handle(high_urgency_event)

        format_string = mock_logger.warning.call_args[0][0]
        assert "HIGH DEMAND AREA IDENTIFIED" in format_string

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_multiple_events_logs_each_separately(self, mock_logger, high_urgency_event, low_urgency_event):
        """Test that multiple events are logged independently."""
        HighDemandAreaEventHandler.handle(high_urgency_event)
        HighDemandAreaEventHandler.handle(low_urgency_event)

        assert mock_logger.warning.call_count == 2

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_extracts_correct_attributes_from_event(self, mock_logger, valid_postal_code):
        """Test that all event attributes are correctly extracted and logged."""
        event = HighDemandAreaIdentifiedEvent(
            postal_code=valid_postal_code,
            population=33456,
            station_count=7,
            urgency_score=72.5,
        )

        HighDemandAreaEventHandler.handle(event)

        args = mock_logger.warning.call_args[0]
        # Verify each parameter is correctly extracted
        assert args[1] == event.postal_code.value
        assert args[2] == event.urgency_score
        assert args[3] == event.population
        assert args[4] == event.station_count


class TestHighDemandAreaEventHandlerStaticMethodBehavior:
    """Test static method characteristics of the handler."""

    def test_handler_class_has_no_instance_variables(self):
        """Test that handler class is stateless with only static methods."""
        handler = HighDemandAreaEventHandler()

        # Should have no instance attributes
        assert len(handler.__dict__) == 0

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_can_be_called_from_instance(self, mock_logger, high_urgency_event):
        """Test that handle method can be called from an instance (though not typical)."""
        handler = HighDemandAreaEventHandler()
        handler.handle(high_urgency_event)

        mock_logger.warning.assert_called_once()

    def test_handler_class_is_instantiable(self):
        """Test that handler class can be instantiated (though typically used statically)."""
        handler = HighDemandAreaEventHandler()

        assert isinstance(handler, HighDemandAreaEventHandler)
        assert hasattr(handler, "handle")


class TestHighDemandAreaEventHandlerEventDataValidation:
    """Test event handler behavior with valid event data structures."""

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_accepts_frozen_dataclass_event(self, mock_logger, high_urgency_event):
        """Test that handler accepts frozen dataclass events (immutable)."""
        # HighDemandAreaIdentifiedEvent is a frozen dataclass
        HighDemandAreaEventHandler.handle(high_urgency_event)

        mock_logger.warning.assert_called_once()

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_with_various_urgency_scores(self, mock_logger, valid_postal_code):
        """Test handler with various urgency score values."""
        urgency_scores = [100.0, 75.0, 50.0, 87.5, 62.25]

        for score in urgency_scores:
            event = HighDemandAreaIdentifiedEvent(
                postal_code=valid_postal_code,
                population=25000,
                station_count=4,
                urgency_score=score,
            )

            HighDemandAreaEventHandler.handle(event)

        assert mock_logger.warning.call_count == 5

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_handle_with_integration_event_characteristics(self, mock_logger, high_urgency_event):
        """Test that handler properly handles integration events (cross-context events)."""
        # Integration events are logged with warning level to alert external systems
        HighDemandAreaEventHandler.handle(high_urgency_event)

        # Verify warning level is used (appropriate for integration events)
        mock_logger.warning.assert_called_once()
        # Verify the format includes clear identification
        format_string = mock_logger.warning.call_args[0][0]
        assert "HIGH DEMAND AREA IDENTIFIED" in format_string


class TestHighDemandAreaEventHandlerComparisonWithOtherHandlers:
    """Test characteristics that distinguish this handler from others."""

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_uses_warning_level_unlike_demand_analysis_handler(self, mock_logger, high_urgency_event):
        """Test that this handler uses warning level (not info) for integration events."""
        HighDemandAreaEventHandler.handle(high_urgency_event)

        # This handler uses warning because it's an integration event
        mock_logger.warning.assert_called_once()
        mock_logger.info.assert_not_called()

    @patch("src.demand.application.event_handlers.high_demand_area_event_handler.logger")
    def test_logs_urgency_score_not_priority_level(self, mock_logger, high_urgency_event):
        """Test that this handler logs urgency score (numeric) not priority level (enum)."""
        HighDemandAreaEventHandler.handle(high_urgency_event)

        args = mock_logger.warning.call_args[0]
        # Second parameter is urgency_score (float)
        assert isinstance(args[2], float)
        # Check format string uses %.2f for urgency score
        format_string = args[0]
        assert "Urgency Score: %.2f" in format_string
