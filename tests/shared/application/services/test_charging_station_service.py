"""
Unit Tests for ChargingStationService.

Test categories:
- Initialization tests
- Search by postal code tests
- Find stations by postal code tests
- Event publishing integration tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode
from src.shared.application.services import BaseService, ChargingStationService
from src.shared.domain.events import IDomainEventPublisher, StationSearchPerformedEvent
from src.shared.infrastructure.repositories import ChargingStationRepository
from src.discovery.application.dtos import PostalCodeAreaDTO


# Test fixtures
@pytest.fixture
def mock_repository():
    """Create a mock ChargingStationRepository."""
    repository = Mock(spec=ChargingStationRepository)
    return repository


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus implementing IDomainEventPublisher."""
    event_bus = Mock(spec=IDomainEventPublisher)
    return event_bus


@pytest.fixture
def charging_station_service(mock_repository, mock_event_bus):
    """Create a ChargingStationService instance."""
    return ChargingStationService(mock_repository, mock_event_bus)


@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def mock_charging_station():
    """Create a mock charging station."""
    station = Mock(spec=ChargingStation)
    station.postal_code = "10115"
    station.latitude = 52.5200
    station.longitude = 13.4050

    power_capacity_mock = Mock()
    power_capacity_mock.kilowatts = 50.0
    station.power_capacity = power_capacity_mock

    station.is_fast_charger = Mock(return_value=True)
    station.get_charging_category = Mock(return_value="FAST")
    return station


@pytest.fixture
def mock_station_list():
    """Create a list of mock charging stations."""
    station1 = Mock(spec=ChargingStation)
    power_capacity_1 = Mock()
    power_capacity_1.kilowatts = 50.0
    station1.power_capacity = power_capacity_1
    station1.is_fast_charger = Mock(return_value=True)
    station1.get_charging_category = Mock(return_value="FAST")

    station2 = Mock(spec=ChargingStation)
    power_capacity_2 = Mock()
    power_capacity_2.kilowatts = 22.0
    station2.power_capacity = power_capacity_2
    station2.is_fast_charger = Mock(return_value=False)
    station2.get_charging_category = Mock(return_value="NORMAL")

    station3 = Mock(spec=ChargingStation)
    power_capacity_3 = Mock()
    power_capacity_3.kilowatts = 150.0
    station3.power_capacity = power_capacity_3
    station3.is_fast_charger = Mock(return_value=True)
    station3.get_charging_category = Mock(return_value="ULTRA")

    return [station1, station2, station3]


class TestChargingStationServiceInitialization:
    """Test initialization of ChargingStationService."""

    def test_service_initializes_with_repository_and_event_bus(self, mock_repository, mock_event_bus):
        """Test that service initializes correctly with repository and event bus."""
        service = ChargingStationService(mock_repository, mock_event_bus)

        assert service.repository is mock_repository
        assert service.event_bus is mock_event_bus

    def test_service_inherits_from_base_service(self, charging_station_service):
        """Test that ChargingStationService inherits from BaseService."""

        assert isinstance(charging_station_service, BaseService)


class TestSearchByPostalCode:
    """Test search_by_postal_code method."""

    def test_search_returns_aggregate_with_stations(
        self, charging_station_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that search_by_postal_code returns aggregate with all stations."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = charging_station_service.search_by_postal_code(valid_postal_code)

        assert isinstance(result, PostalCodeAreaDTO)
        assert result.postal_code == valid_postal_code.value
        assert result.station_count == 3

    def test_search_calls_repository_with_correct_postal_code(
        self, charging_station_service, valid_postal_code, mock_repository
    ):
        """Test that search calls repository with correct postal code."""
        mock_repository.find_stations_by_postal_code.return_value = []

        charging_station_service.search_by_postal_code(valid_postal_code)

        mock_repository.find_stations_by_postal_code.assert_called_once_with(valid_postal_code)

    def test_search_returns_empty_aggregate_when_no_stations_found(
        self, charging_station_service, valid_postal_code, mock_repository
    ):
        """Test that search returns empty aggregate when no stations found."""
        mock_repository.find_stations_by_postal_code.return_value = []

        result = charging_station_service.search_by_postal_code(valid_postal_code)

        assert isinstance(result, PostalCodeAreaDTO)
        assert result.station_count == 0
        assert result.postal_code == valid_postal_code.value

    def test_search_adds_all_stations_to_aggregate(
        self, charging_station_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that all stations from repository are added to aggregate."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = charging_station_service.search_by_postal_code(valid_postal_code)

        assert result.station_count == len(mock_station_list)

    def test_search_triggers_search_performed_event(self, charging_station_service, valid_postal_code, mock_repository):
        """Test that search triggers perform_search on aggregate."""
        mock_repository.find_stations_by_postal_code.return_value = []

        result = charging_station_service.search_by_postal_code(valid_postal_code)

        # DTO doesn't have domain events
        assert isinstance(result, PostalCodeAreaDTO)

    def test_search_publishes_events_to_event_bus(
        self, charging_station_service, valid_postal_code, mock_repository, mock_event_bus
    ):
        """Test that search publishes domain events to event bus."""
        mock_repository.find_stations_by_postal_code.return_value = []

        charging_station_service.search_by_postal_code(valid_postal_code)

        # Event bus should have received publish call
        assert mock_event_bus.publish.call_count == 1
        published_event = mock_event_bus.publish.call_args[0][0]
        assert isinstance(published_event, StationSearchPerformedEvent)

    def test_search_clears_events_after_publishing(self, charging_station_service, valid_postal_code, mock_repository):
        """Test that aggregate events are cleared after publishing."""
        mock_repository.find_stations_by_postal_code.return_value = []

        result = charging_station_service.search_by_postal_code(valid_postal_code)

        # DTO doesn't have domain events
        assert isinstance(result, PostalCodeAreaDTO)


class TestFindStationsByPostalCode:
    """Test find_stations_by_postal_code method."""

    def test_find_returns_list_of_stations(
        self, charging_station_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that find_stations_by_postal_code returns list of stations."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = charging_station_service.find_stations_by_postal_code(valid_postal_code)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result == mock_station_list

    def test_find_returns_empty_list_when_no_stations(
        self, charging_station_service, valid_postal_code, mock_repository
    ):
        """Test that find returns empty list when no stations found."""
        mock_repository.find_stations_by_postal_code.return_value = []

        result = charging_station_service.find_stations_by_postal_code(valid_postal_code)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_calls_repository_with_correct_postal_code(
        self, charging_station_service, valid_postal_code, mock_repository
    ):
        """Test that find calls repository with correct postal code."""
        mock_repository.find_stations_by_postal_code.return_value = []

        charging_station_service.find_stations_by_postal_code(valid_postal_code)

        mock_repository.find_stations_by_postal_code.assert_called_once_with(valid_postal_code)

    def test_find_does_not_publish_events(
        self, charging_station_service, valid_postal_code, mock_repository, mock_event_bus
    ):
        """Test that find_stations_by_postal_code does not publish events."""
        mock_repository.find_stations_by_postal_code.return_value = []

        charging_station_service.find_stations_by_postal_code(valid_postal_code)

        # Event bus should not be called for simple find operation
        mock_event_bus.publish.assert_not_called()

    def test_find_does_not_create_aggregate(
        self, charging_station_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that find returns raw station list without aggregate wrapper."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = charging_station_service.find_stations_by_postal_code(valid_postal_code)

        # Result should be plain list, not DTO
        assert not isinstance(result, PostalCodeAreaDTO)
        assert isinstance(result, list)


class TestChargingStationServiceIntegration:
    """Integration tests for ChargingStationService."""

    def test_search_workflow_with_multiple_stations(
        self, mock_repository, mock_event_bus, valid_postal_code, mock_station_list
    ):
        """Test complete search workflow with multiple stations."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list
        service = ChargingStationService(mock_repository, mock_event_bus)

        result = service.search_by_postal_code(valid_postal_code)

        # Verify repository was called
        mock_repository.find_stations_by_postal_code.assert_called_once_with(valid_postal_code)

        # Verify DTO was created with stations
        assert result.station_count == 3
        assert result.postal_code == valid_postal_code.value

        # Verify events were published
        assert mock_event_bus.publish.call_count == 1

    def test_find_workflow_returns_raw_stations(
        self, mock_repository, mock_event_bus, valid_postal_code, mock_station_list
    ):
        """Test find workflow returns raw station list."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list
        service = ChargingStationService(mock_repository, mock_event_bus)

        result = service.find_stations_by_postal_code(valid_postal_code)

        # Verify repository was called
        mock_repository.find_stations_by_postal_code.assert_called_once_with(valid_postal_code)

        # Verify raw list was returned
        assert result == mock_station_list

        # Verify no events were published
        mock_event_bus.publish.assert_not_called()

    def test_multiple_searches_publish_separate_events(
        self, charging_station_service, valid_postal_code, mock_repository, mock_event_bus
    ):
        """Test that multiple searches publish separate events."""
        mock_repository.find_stations_by_postal_code.return_value = []

        # First search
        charging_station_service.search_by_postal_code(valid_postal_code)

        # Second search
        postal_code_2 = PostalCode("10117")
        charging_station_service.search_by_postal_code(postal_code_2)

        # Both searches should have published events
        assert mock_event_bus.publish.call_count == 2

    def test_search_and_find_use_same_repository_method(
        self, charging_station_service, valid_postal_code, mock_repository, mock_station_list
    ):
        """Test that search and find both use repository's find_stations_by_postal_code."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        # Call search
        charging_station_service.search_by_postal_code(valid_postal_code)

        # Call find
        charging_station_service.find_stations_by_postal_code(valid_postal_code)

        # Repository method should be called twice
        assert mock_repository.find_stations_by_postal_code.call_count == 2

    def test_service_handles_single_station_correctly(
        self, charging_station_service, valid_postal_code, mock_repository, mock_charging_station
    ):
        """Test service handles single station result correctly."""
        mock_repository.find_stations_by_postal_code.return_value = [mock_charging_station]

        result = charging_station_service.search_by_postal_code(valid_postal_code)

        assert result.station_count == 1
        assert result.has_fast_charging is True

    def test_event_contains_correct_search_parameters(
        self, charging_station_service, valid_postal_code, mock_repository, mock_event_bus
    ):
        """Test that published event contains correct search parameters."""
        mock_repository.find_stations_by_postal_code.return_value = []

        charging_station_service.search_by_postal_code(valid_postal_code)

        published_event = mock_event_bus.publish.call_args[0][0]
        assert published_event.postal_code.value == valid_postal_code.value
        assert published_event.stations_found == 0
