"""
Unit Tests for StationSearchEventHandler.

Test categories:
- handle method tests
- handle_failure method tests
- handle_no_results method tests
- handle_stations_found method tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import patch

import pytest

from src.shared.application.event_handlers import StationSearchEventHandler
from src.shared.domain.events import (
    NoStationsFoundEvent,
    StationSearchFailedEvent,
    StationSearchPerformedEvent,
    StationsFoundEvent,
)
from src.shared.domain.value_objects import PostalCode


@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


class TestStationSearchEventHandlerHandle:
    """Test handle method."""

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_logs_search_performed(self, mock_logger, valid_postal_code):
        """Test that handle method logs search performed event."""
        event = StationSearchPerformedEvent(postal_code=valid_postal_code, stations_found=5, search_parameters={})

        StationSearchEventHandler.handle(event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Station search performed for postal code: %s (found %d stations)",
            valid_postal_code.value,
            5,
        )

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_logs_zero_stations(self, mock_logger, valid_postal_code):
        """Test that handle method logs when zero stations found."""
        event = StationSearchPerformedEvent(postal_code=valid_postal_code, stations_found=0, search_parameters={})

        StationSearchEventHandler.handle(event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Station search performed for postal code: %s (found %d stations)",
            valid_postal_code.value,
            0,
        )


class TestStationSearchEventHandlerHandleFailure:
    """Test handle_failure method."""

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_failure_logs_error_with_type(self, mock_logger, valid_postal_code):
        """Test that handle_failure logs error with error type."""
        event = StationSearchFailedEvent(
            postal_code=valid_postal_code, error_message="Connection timeout", error_type="NetworkError"
        )

        StationSearchEventHandler.handle_failure(event)

        mock_logger.error.assert_called_once_with(
            "[EVENT] Station search failed for postal code: %s - Error: %s (Type: %s)",
            valid_postal_code.value,
            "Connection timeout",
            "NetworkError",
        )

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_failure_logs_error_without_type(self, mock_logger, valid_postal_code):
        """Test that handle_failure logs error without error type."""
        event = StationSearchFailedEvent(postal_code=valid_postal_code, error_message="Generic error", error_type=None)

        StationSearchEventHandler.handle_failure(event)

        mock_logger.error.assert_called_once_with(
            "[EVENT] Station search failed for postal code: %s - Error: %s (Type: %s)",
            valid_postal_code.value,
            "Generic error",
            "Unknown",
        )


class TestStationSearchEventHandlerHandleNoResults:
    """Test handle_no_results method."""

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_no_results_logs_warning(self, mock_logger, valid_postal_code):
        """Test that handle_no_results logs warning for infrastructure gap."""
        event = NoStationsFoundEvent(postal_code=valid_postal_code)

        StationSearchEventHandler.handle_no_results(event)

        mock_logger.warning.assert_called_once_with(
            "[EVENT] No stations found for postal code: %s - Infrastructure gap identified",
            valid_postal_code.value,
        )


class TestStationSearchEventHandlerHandleStationsFound:
    """Test handle_stations_found method."""

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_stations_found_logs_discovery(self, mock_logger, valid_postal_code):
        """Test that handle_stations_found logs station discovery."""
        event = StationsFoundEvent(postal_code=valid_postal_code, stations_found=3)

        StationSearchEventHandler.handle_stations_found(event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Stations found for postal code: %s (%d stations discovered)",
            valid_postal_code.value,
            3,
        )

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_handle_stations_found_logs_single_station(self, mock_logger, valid_postal_code):
        """Test that handle_stations_found logs single station discovery."""
        event = StationsFoundEvent(postal_code=valid_postal_code, stations_found=1)

        StationSearchEventHandler.handle_stations_found(event)

        mock_logger.info.assert_called_once_with(
            "[EVENT] Stations found for postal code: %s (%d stations discovered)",
            valid_postal_code.value,
            1,
        )


class TestStationSearchEventHandlerIntegration:
    """Integration tests for StationSearchEventHandler."""

    @patch("src.shared.application.event_handlers.station_search_event_handler.logger")
    def test_all_handlers_can_be_called(self, mock_logger, valid_postal_code):
        """Test that all handler methods can be called successfully."""
        # Create events
        search_event = StationSearchPerformedEvent(
            postal_code=valid_postal_code, stations_found=5, search_parameters={}
        )
        failure_event = StationSearchFailedEvent(
            postal_code=valid_postal_code, error_message="Error", error_type="Type"
        )
        no_results_event = NoStationsFoundEvent(postal_code=valid_postal_code)
        found_event = StationsFoundEvent(postal_code=valid_postal_code, stations_found=3)

        # Call all handlers
        StationSearchEventHandler.handle(search_event)
        StationSearchEventHandler.handle_failure(failure_event)
        StationSearchEventHandler.handle_no_results(no_results_event)
        StationSearchEventHandler.handle_stations_found(found_event)

        # Verify all were called
        assert mock_logger.info.call_count == 2
        assert mock_logger.error.call_count == 1
        assert mock_logger.warning.call_count == 1
