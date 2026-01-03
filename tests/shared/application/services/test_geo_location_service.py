"""
Unit Tests for GeoLocationService.

Test categories:
- Initialization tests
- Get geolocation data for postal code tests
- Get all postal codes tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from src.shared.application.services import BaseService, GeoLocationService
from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.domain.events import IDomainEventPublisher
from src.shared.infrastructure.repositories import GeoDataRepository


# Test fixtures
@pytest.fixture
def mock_repository():
    """Create a mock GeoDataRepository."""
    repository = Mock(spec=GeoDataRepository)
    # Configure the mock to have the necessary methods
    repository.fetch_geolocation_data = Mock()
    repository.get_all_postal_codes = Mock()
    return repository


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus implementing IDomainEventPublisher."""
    event_bus = Mock(spec=IDomainEventPublisher)
    return event_bus


@pytest.fixture
def geo_location_service(mock_repository, mock_event_bus):
    """Create a GeoLocationService instance."""
    return GeoLocationService(mock_repository, mock_event_bus)


@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def mock_geo_location():
    """Create a mock GeoLocation."""
    geo_location = Mock(spec=GeoLocation)
    geo_location.latitude = 52.5200
    geo_location.longitude = 13.4050
    geo_location.postal_code = "10115"
    return geo_location


@pytest.fixture
def postal_code_list():
    """Create a list of postal codes."""
    return [10115, 10117, 10119, 10178, 10179]


class TestGeoLocationServiceInitialization:
    """Test initialization of GeoLocationService."""

    def test_service_initializes_with_repository_and_event_bus(self, mock_repository, mock_event_bus):
        """Test that service initializes correctly with repository and event bus."""
        service = GeoLocationService(mock_repository, mock_event_bus)

        assert service.repository is mock_repository
        assert service.event_bus is mock_event_bus

    def test_service_inherits_from_base_service(self, geo_location_service):
        """Test that GeoLocationService inherits from BaseService."""
        assert isinstance(geo_location_service, BaseService)


class TestGetGeolocationDataForPostalCode:
    """Test get_geolocation_data_for_postal_code method."""

    def test_get_geolocation_returns_geo_location_object(
        self, geo_location_service, valid_postal_code, mock_geo_location, mock_repository
    ):
        """Test that get_geolocation_data_for_postal_code returns GeoLocation object."""
        mock_repository.fetch_geolocation_data.return_value = mock_geo_location

        result = geo_location_service.get_geolocation_data_for_postal_code(valid_postal_code)

        assert result is mock_geo_location
        assert result.latitude == 52.5200
        assert result.longitude == 13.4050

    def test_get_geolocation_calls_repository_with_correct_postal_code(
        self, geo_location_service, valid_postal_code, mock_repository
    ):
        """Test that method calls repository with correct postal code."""
        mock_repository.fetch_geolocation_data.return_value = None

        geo_location_service.get_geolocation_data_for_postal_code(valid_postal_code)

        mock_repository.fetch_geolocation_data.assert_called_once_with(valid_postal_code)

    def test_get_geolocation_returns_none_when_not_found(
        self, geo_location_service, valid_postal_code, mock_repository
    ):
        """Test that method returns None when postal code not found."""
        mock_repository.fetch_geolocation_data.return_value = None

        result = geo_location_service.get_geolocation_data_for_postal_code(valid_postal_code)

        assert result is None

    def test_get_geolocation_handles_different_postal_codes(
        self, geo_location_service, mock_repository, mock_geo_location
    ):
        """Test that method handles different postal codes correctly."""
        postal_code_1 = PostalCode("10115")
        postal_code_2 = PostalCode("10117")

        mock_repository.fetch_geolocation_data.return_value = mock_geo_location

        result_1 = geo_location_service.get_geolocation_data_for_postal_code(postal_code_1)
        result_2 = geo_location_service.get_geolocation_data_for_postal_code(postal_code_2)

        assert result_1 is mock_geo_location
        assert result_2 is mock_geo_location
        assert mock_repository.fetch_geolocation_data.call_count == 2

    def test_get_geolocation_does_not_publish_events(
        self, geo_location_service, valid_postal_code, mock_repository, mock_event_bus, mock_geo_location
    ):
        """Test that get_geolocation_data_for_postal_code does not publish events."""
        mock_repository.fetch_geolocation_data.return_value = mock_geo_location

        geo_location_service.get_geolocation_data_for_postal_code(valid_postal_code)

        # Event bus should not be called for simple query operation
        mock_event_bus.publish.assert_not_called()


class TestGetAllPostalCodes:
    """Test get_all_plzs method."""

    def test_get_all_plzs_returns_list_of_integers(self, geo_location_service, postal_code_list, mock_repository):
        """Test that get_all_plzs returns list of postal code integers."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list

        result = geo_location_service.get_all_plzs()

        assert isinstance(result, list)
        assert len(result) == 5
        assert result == postal_code_list
        assert all(isinstance(plz, int) for plz in result)

    def test_get_all_plzs_returns_empty_list_when_no_data(self, geo_location_service, mock_repository):
        """Test that get_all_plzs returns empty list when no data available."""
        mock_repository.get_all_postal_codes.return_value = []

        result = geo_location_service.get_all_plzs()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_all_plzs_calls_repository_method(self, geo_location_service, mock_repository):
        """Test that get_all_plzs calls repository's get_all_postal_codes."""
        mock_repository.get_all_postal_codes.return_value = []

        geo_location_service.get_all_plzs()

        mock_repository.get_all_postal_codes.assert_called_once()

    def test_get_all_plzs_does_not_publish_events(
        self, geo_location_service, mock_repository, mock_event_bus, postal_code_list
    ):
        """Test that get_all_plzs does not publish events."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list

        geo_location_service.get_all_plzs()

        # Event bus should not be called for simple query operation
        mock_event_bus.publish.assert_not_called()

    def test_get_all_plzs_returns_large_list(self, geo_location_service, mock_repository):
        """Test that get_all_plzs can handle large lists of postal codes."""
        large_list = list(range(10000, 20000))
        mock_repository.get_all_postal_codes.return_value = large_list

        result = geo_location_service.get_all_plzs()

        assert len(result) == 10000
        assert result == large_list


class TestGeoLocationServiceIntegration:
    """Integration tests for GeoLocationService."""

    def test_service_workflow_get_geolocation_for_existing_postal_code(
        self, mock_repository, mock_event_bus, valid_postal_code, mock_geo_location
    ):
        """Test complete workflow for retrieving geolocation data."""
        mock_repository.fetch_geolocation_data.return_value = mock_geo_location
        service = GeoLocationService(mock_repository, mock_event_bus)

        result = service.get_geolocation_data_for_postal_code(valid_postal_code)

        # Verify repository was called
        mock_repository.fetch_geolocation_data.assert_called_once_with(valid_postal_code)

        # Verify result is correct
        assert result is mock_geo_location

        # Verify no events were published
        mock_event_bus.publish.assert_not_called()

    def test_service_workflow_get_all_postal_codes(self, mock_repository, mock_event_bus, postal_code_list):
        """Test complete workflow for retrieving all postal codes."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list
        service = GeoLocationService(mock_repository, mock_event_bus)

        result = service.get_all_plzs()

        # Verify repository was called
        mock_repository.get_all_postal_codes.assert_called_once()

        # Verify result is correct
        assert result == postal_code_list

        # Verify no events were published
        mock_event_bus.publish.assert_not_called()

    def test_multiple_geolocation_queries_call_repository_each_time(
        self, geo_location_service, mock_repository, mock_geo_location
    ):
        """Test that multiple queries each call the repository."""
        mock_repository.fetch_geolocation_data.return_value = mock_geo_location

        postal_codes = [PostalCode("10115"), PostalCode("10117"), PostalCode("10119")]

        for postal_code in postal_codes:
            geo_location_service.get_geolocation_data_for_postal_code(postal_code)

        assert mock_repository.fetch_geolocation_data.call_count == 3

    def test_service_handles_mixed_operations(
        self, geo_location_service, mock_repository, mock_geo_location, postal_code_list
    ):
        """Test service handles mixed get_geolocation and get_all_plzs operations."""
        mock_repository.fetch_geolocation_data.return_value = mock_geo_location
        mock_repository.get_all_postal_codes.return_value = postal_code_list

        # Get all postal codes
        all_plzs = geo_location_service.get_all_plzs()
        assert len(all_plzs) == 5

        # Get geolocation for specific postal code
        result = geo_location_service.get_geolocation_data_for_postal_code(PostalCode("10115"))
        assert result is mock_geo_location

        # Verify both repository methods were called
        mock_repository.get_all_postal_codes.assert_called_once()
        mock_repository.fetch_geolocation_data.assert_called_once()

    def test_service_only_uses_repository_no_direct_event_publishing(
        self, geo_location_service, mock_repository, mock_event_bus, valid_postal_code, mock_geo_location
    ):
        """Test that service is purely a query service with no event publishing."""
        mock_repository.fetch_geolocation_data.return_value = mock_geo_location
        mock_repository.get_all_postal_codes.return_value = [10115, 10117]

        # Perform both operations
        geo_location_service.get_geolocation_data_for_postal_code(valid_postal_code)
        geo_location_service.get_all_plzs()

        # Verify no events were published for either operation
        mock_event_bus.publish.assert_not_called()
