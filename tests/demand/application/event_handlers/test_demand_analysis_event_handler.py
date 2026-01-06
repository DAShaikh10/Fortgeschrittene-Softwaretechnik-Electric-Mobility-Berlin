"""
Unit Tests for DemandAnalysisEventHandler.

Test categories:
- Event handling tests
- Logging validation tests
- Edge cases and data variations
"""

# pylint: disable=redefined-outer-name

from unittest.mock import patch

import pytest

from src.shared.domain.value_objects import PostalCode
from src.demand.domain.enums import PriorityLevel
from src.demand.domain.events import DemandAnalysisCalculatedEvent
from src.demand.domain.value_objects import DemandPriority
from src.demand.application.event_handlers import DemandAnalysisEventHandler


# Test fixtures
@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def high_demand_priority():
    """Create a high priority demand priority value object."""
    return DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)


@pytest.fixture
def medium_demand_priority():
    """Create a medium priority demand priority value object."""
    return DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3500.0)


@pytest.fixture
def low_demand_priority():
    """Create a low priority demand priority value object."""
    return DemandPriority(level=PriorityLevel.LOW, residents_per_station=1500.0)


@pytest.fixture
def high_priority_event(valid_postal_code, high_demand_priority):
    """Create a demand analysis event with high priority."""
    return DemandAnalysisCalculatedEvent(
        postal_code=valid_postal_code,
        population=30000,
        station_count=5,
        demand_priority=high_demand_priority,
    )


@pytest.fixture
def medium_priority_event(valid_postal_code, medium_demand_priority):
    """Create a demand analysis event with medium priority."""
    return DemandAnalysisCalculatedEvent(
        postal_code=valid_postal_code,
        population=14000,
        station_count=4,
        demand_priority=medium_demand_priority,
    )


@pytest.fixture
def low_priority_event(valid_postal_code, low_demand_priority):
    """Create a demand analysis event with low priority."""
    return DemandAnalysisCalculatedEvent(
        postal_code=valid_postal_code,
        population=9000,
        station_count=6,
        demand_priority=low_demand_priority,
    )


class TestDemandAnalysisEventHandlerBasicFunctionality:
    """Test basic event handler functionality."""

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_high_priority_event_with_correct_format(self, mock_logger, high_priority_event):
        """Test that handle method logs high priority events with proper formatting."""
        DemandAnalysisEventHandler.handle(high_priority_event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Demand analysis calculated for postal code: %s | "
            "Priority: %s | Population: %d | Stations: %d | Residents/Station: %.1f",
            "10115",
            "High",
            30000,
            5,
            6000.0,
        )

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_medium_priority_event(self, mock_logger, medium_priority_event):
        """Test that handle method logs medium priority events correctly."""
        DemandAnalysisEventHandler.handle(medium_priority_event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Demand analysis calculated for postal code: %s | "
            "Priority: %s | Population: %d | Stations: %d | Residents/Station: %.1f",
            "10115",
            "Medium",
            14000,
            4,
            3500.0,
        )

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_low_priority_event(self, mock_logger, low_priority_event):
        """Test that handle method logs low priority events correctly."""
        DemandAnalysisEventHandler.handle(low_priority_event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Demand analysis calculated for postal code: %s | "
            "Priority: %s | Population: %d | Stations: %d | Residents/Station: %.1f",
            "10115",
            "Low",
            9000,
            6,
            1500.0,
        )

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_returns_none(self, high_priority_event):
        """Test that handle method returns None."""
        result = DemandAnalysisEventHandler.handle(high_priority_event)

        assert result is None

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_is_static_method(self, mock_logger, high_priority_event):
        """Test that handle can be called as a static method without instantiation."""
        # Call without creating an instance
        DemandAnalysisEventHandler.handle(high_priority_event)

        # Verify it was called
        assert mock_logger.info.call_count == 1


class TestDemandAnalysisEventHandlerWithVariousPostalCodes:
    """Test event handler with different postal codes."""

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_different_postal_code_10xxx(self, mock_logger, high_demand_priority):
        """Test logging with postal code starting with 10."""
        postal_code = PostalCode("10178")
        event = DemandAnalysisCalculatedEvent(
            postal_code=postal_code,
            population=25000,
            station_count=3,
            demand_priority=high_demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[1] == "10178"

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_postal_code_12xxx(self, mock_logger, medium_demand_priority):
        """Test logging with postal code starting with 12."""
        postal_code = PostalCode("12345")
        event = DemandAnalysisCalculatedEvent(
            postal_code=postal_code,
            population=18000,
            station_count=5,
            demand_priority=medium_demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[1] == "12345"

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_postal_code_13xxx(self, mock_logger, low_demand_priority):
        """Test logging with postal code starting with 13."""
        postal_code = PostalCode("13579")
        event = DemandAnalysisCalculatedEvent(
            postal_code=postal_code,
            population=10000,
            station_count=7,
            demand_priority=low_demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[1] == "13579"

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_postal_code_14xxx(self, mock_logger, high_demand_priority):
        """Test logging with postal code starting with 14."""
        postal_code = PostalCode("14195")
        event = DemandAnalysisCalculatedEvent(
            postal_code=postal_code,
            population=22000,
            station_count=2,
            demand_priority=high_demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[1] == "14195"


class TestDemandAnalysisEventHandlerEdgeCases:
    """Test event handler with edge cases and boundary values."""

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_zero_stations(self, mock_logger, valid_postal_code):
        """Test logging when station count is zero (indicates infinite residents per station)."""
        demand_priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=50000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=50000,
            station_count=0,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Demand analysis calculated for postal code: %s | "
            "Priority: %s | Population: %d | Stations: %d | Residents/Station: %.1f",
            "10115",
            "High",
            50000,
            0,
            50000.0,
        )

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_single_station(self, mock_logger, valid_postal_code):
        """Test logging when there is exactly one station."""
        demand_priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=15000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=15000,
            station_count=1,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[4] == 1  # station_count

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_large_population(self, mock_logger, valid_postal_code):
        """Test logging with very large population."""
        demand_priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=100000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=1000000,
            station_count=10,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[3] == 1000000  # population

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_many_stations(self, mock_logger, valid_postal_code):
        """Test logging with large number of stations."""
        demand_priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=100.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=5000,
            station_count=50,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[4] == 50  # station_count

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_fractional_residents_per_station(self, mock_logger, valid_postal_code):
        """Test that residents per station is logged with one decimal place."""
        demand_priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=2345.6789)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=11728,
            station_count=5,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        # Check the format string uses %.1f
        format_string = mock_logger.info.call_args[0][0]
        assert "%.1f" in format_string
        # Check the actual value
        args = mock_logger.info.call_args[0]
        assert args[5] == 2345.6789

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_event_with_exact_threshold_values(self, mock_logger, valid_postal_code):
        """Test logging with residents per station at exact priority threshold (5000)."""
        demand_priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=5000.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=25000,
            station_count=5,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        mock_logger.info.assert_called_once()
        args = mock_logger.info.call_args[0]
        assert args[5] == 5000.0


class TestDemandAnalysisEventHandlerLoggerIntegration:
    """Test integration with the logging system."""

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_calls_logger_info_not_warning_or_error(self, mock_logger, high_priority_event):
        """Test that handler uses info level logging, not warning or error."""
        DemandAnalysisEventHandler.handle(high_priority_event)

        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()
        mock_logger.debug.assert_not_called()

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_logs_with_event_prefix(self, mock_logger, high_priority_event):
        """Test that log message includes [EVENT] prefix."""
        DemandAnalysisEventHandler.handle(high_priority_event)

        format_string = mock_logger.info.call_args[0][0]
        assert format_string.startswith("[EVENT]")

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_multiple_events_logs_each_separately(self, mock_logger, high_priority_event, low_priority_event):
        """Test that multiple events are logged independently."""
        DemandAnalysisEventHandler.handle(high_priority_event)
        DemandAnalysisEventHandler.handle(low_priority_event)

        assert mock_logger.info.call_count == 2

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_extracts_correct_attributes_from_event(self, mock_logger, valid_postal_code):
        """Test that all event attributes are correctly extracted and logged."""
        demand_priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=4321.0)
        event = DemandAnalysisCalculatedEvent(
            postal_code=valid_postal_code,
            population=12963,
            station_count=3,
            demand_priority=demand_priority,
        )

        DemandAnalysisEventHandler.handle(event)

        args = mock_logger.info.call_args[0]
        # Verify each parameter is correctly extracted
        assert args[1] == event.postal_code.value
        assert args[2] == event.demand_priority.level.value
        assert args[3] == event.population
        assert args[4] == event.station_count
        assert args[5] == event.demand_priority.residents_per_station


class TestDemandAnalysisEventHandlerStaticMethodBehavior:
    """Test static method characteristics of the handler."""

    def test_handler_class_has_no_instance_variables(self):
        """Test that handler class is stateless with only static methods."""
        handler = DemandAnalysisEventHandler()

        # Should have no instance attributes
        assert len(handler.__dict__) == 0

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_can_be_called_from_instance(self, mock_logger, high_priority_event):
        """Test that handle method can be called from an instance (though not typical)."""
        handler = DemandAnalysisEventHandler()
        handler.handle(high_priority_event)

        mock_logger.info.assert_called_once()

    def test_handler_class_is_instantiable(self):
        """Test that handler class can be instantiated (though typically used statically)."""
        handler = DemandAnalysisEventHandler()

        assert isinstance(handler, DemandAnalysisEventHandler)
        assert hasattr(handler, "handle")


class TestDemandAnalysisEventHandlerEventDataValidation:
    """Test event handler behavior with valid event data structures."""

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_accepts_frozen_dataclass_event(self, mock_logger, high_priority_event):
        """Test that handler accepts frozen dataclass events (immutable)."""
        # DemandAnalysisCalculatedEvent is a frozen dataclass
        DemandAnalysisEventHandler.handle(high_priority_event)

        mock_logger.info.assert_called_once()

    @patch("src.demand.application.event_handlers.demand_analysis_event_handler.logger")
    def test_handle_with_all_priority_levels(self, mock_logger, valid_postal_code):
        """Test handler with all three priority levels."""
        priority_levels = [
            (PriorityLevel.HIGH, 7000.0),
            (PriorityLevel.MEDIUM, 3000.0),
            (PriorityLevel.LOW, 1000.0),
        ]

        for level, ratio in priority_levels:
            demand_priority = DemandPriority(level=level, residents_per_station=ratio)
            event = DemandAnalysisCalculatedEvent(
                postal_code=valid_postal_code,
                population=10000,
                station_count=2,
                demand_priority=demand_priority,
            )

            DemandAnalysisEventHandler.handle(event)

        assert mock_logger.info.call_count == 3
