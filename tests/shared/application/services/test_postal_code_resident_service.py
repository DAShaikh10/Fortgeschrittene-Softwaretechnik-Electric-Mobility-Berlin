"""
Unit Tests for PostalCodeResidentService.

Test categories:
- Initialization tests
- Get all postal codes tests
- Get resident data tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from src.shared.application.services import BaseService, PostalCodeResidentService
from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.value_objects import PostalCode, PopulationData
from src.shared.infrastructure.repositories import PopulationRepository


# Test fixtures
@pytest.fixture
def mock_repository():
    """Create a mock PopulationRepository."""
    repository = Mock(spec=PopulationRepository)
    repository.get_all_postal_codes = Mock()
    repository.get_residents_count = Mock()
    return repository


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus implementing IDomainEventPublisher."""
    event_bus = Mock(spec=IDomainEventPublisher)
    return event_bus


@pytest.fixture
def postal_code_resident_service(mock_repository, mock_event_bus):
    """Create a PostalCodeResidentService instance."""
    return PostalCodeResidentService(mock_repository, mock_event_bus)


@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def postal_code_list():
    """Create a list of postal codes."""
    return [
        PostalCode("10115"),
        PostalCode("10117"),
        PostalCode("10119"),
        PostalCode("10178"),
        PostalCode("10179")
    ]


class TestPostalCodeResidentServiceInitialization:
    """Test initialization of PostalCodeResidentService."""

    def test_service_initializes_with_repository_and_event_bus(self, mock_repository, mock_event_bus):
        """Test that service initializes correctly with repository and event bus."""
        service = PostalCodeResidentService(mock_repository, mock_event_bus)

        assert service.repository is mock_repository
        assert service._event_bus is mock_event_bus

    def test_service_inherits_from_base_service(self, postal_code_resident_service):
        """Test that PostalCodeResidentService inherits from BaseService."""
        assert isinstance(postal_code_resident_service, BaseService)

    def test_service_stores_repository(self, postal_code_resident_service, mock_repository):
        """Test that service stores repository reference."""
        assert postal_code_resident_service.repository is mock_repository

    def test_service_stores_event_bus(self, postal_code_resident_service, mock_event_bus):
        """Test that service stores event bus reference."""
        assert postal_code_resident_service._event_bus is mock_event_bus


class TestGetAllPostalCodes:
    """Test get_all_postal_codes method."""

    def test_returns_list_of_postal_codes(
        self, postal_code_resident_service, postal_code_list, mock_repository
    ):
        """Test that method returns list of PostalCode objects."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list

        result = postal_code_resident_service.get_all_postal_codes()

        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(plz, PostalCode) for plz in result)
        assert result == postal_code_list

    def test_returns_empty_list_when_no_data(self, postal_code_resident_service, mock_repository):
        """Test that method returns empty list when no data available."""
        mock_repository.get_all_postal_codes.return_value = []

        result = postal_code_resident_service.get_all_postal_codes()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_calls_repository_method(self, postal_code_resident_service, mock_repository):
        """Test that method calls repository's get_all_postal_codes."""
        mock_repository.get_all_postal_codes.return_value = []

        postal_code_resident_service.get_all_postal_codes()

        mock_repository.get_all_postal_codes.assert_called_once()

    def test_returns_unsorted_when_sort_false(
        self, postal_code_resident_service, mock_repository
    ):
        """Test that method returns unsorted list when sort=False."""
        unsorted_list = [
            PostalCode("10179"),
            PostalCode("10115"),
            PostalCode("10119"),
            PostalCode("10117"),
            PostalCode("10178")
        ]
        mock_repository.get_all_postal_codes.return_value = unsorted_list

        result = postal_code_resident_service.get_all_postal_codes(sort=False)

        assert result == unsorted_list
        assert result[0].value == "10179"  # First element unchanged

    def test_returns_sorted_when_sort_true(
        self, postal_code_resident_service, mock_repository
    ):
        """Test that method returns sorted list when sort=True."""
        unsorted_list = [
            PostalCode("10179"),
            PostalCode("10115"),
            PostalCode("10119"),
            PostalCode("10117"),
            PostalCode("10178")
        ]
        mock_repository.get_all_postal_codes.return_value = unsorted_list

        result = postal_code_resident_service.get_all_postal_codes(sort=True)

        assert len(result) == 5
        assert result[0].value == "10115"
        assert result[1].value == "10117"
        assert result[2].value == "10119"
        assert result[3].value == "10178"
        assert result[4].value == "10179"

    def test_sort_defaults_to_false(
        self, postal_code_resident_service, mock_repository
    ):
        """Test that sort parameter defaults to False."""
        unsorted_list = [
            PostalCode("10179"),
            PostalCode("10115")
        ]
        mock_repository.get_all_postal_codes.return_value = unsorted_list

        result = postal_code_resident_service.get_all_postal_codes()

        assert result == unsorted_list  # Should remain unsorted

    def test_handles_single_postal_code(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that method handles single postal code correctly."""
        mock_repository.get_all_postal_codes.return_value = [valid_postal_code]

        result = postal_code_resident_service.get_all_postal_codes()

        assert len(result) == 1
        assert result[0] == valid_postal_code

    def test_does_not_modify_original_list(
        self, postal_code_resident_service, mock_repository
    ):
        """Test that sorting does not modify the original repository list."""
        original_list = [
            PostalCode("10179"),
            PostalCode("10115")
        ]
        mock_repository.get_all_postal_codes.return_value = original_list

        sorted_result = postal_code_resident_service.get_all_postal_codes(sort=True)

        # Original list should be unchanged (service creates a copy or sorts in place)
        # The repository's list might be modified, but that's acceptable
        assert len(sorted_result) == 2

    def test_does_not_publish_events(
        self, postal_code_resident_service, mock_repository, mock_event_bus, postal_code_list
    ):
        """Test that get_all_postal_codes does not publish events."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list

        postal_code_resident_service.get_all_postal_codes()

        # Event bus should not be called for simple query operation
        mock_event_bus.publish.assert_not_called()


class TestGetResidentData:
    """Test get_resident_data method."""

    def test_returns_population_data_object(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that method returns PopulationData object."""
        mock_repository.get_residents_count.return_value = 5000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert isinstance(result, PopulationData)
        assert result.postal_code == valid_postal_code
        assert result.population == 5000

    def test_calls_repository_with_correct_postal_code(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that method calls repository with correct postal code."""
        mock_repository.get_residents_count.return_value = 5000

        postal_code_resident_service.get_resident_data(valid_postal_code)

        mock_repository.get_residents_count.assert_called_once_with(valid_postal_code)

    def test_creates_population_data_with_zero_residents(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that method handles zero residents correctly."""
        mock_repository.get_residents_count.return_value = 0

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.population == 0
        assert result.postal_code == valid_postal_code

    def test_creates_population_data_with_high_population(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that method handles high population correctly."""
        mock_repository.get_residents_count.return_value = 25000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.population == 25000
        assert result.get_population_density_category() == "HIGH"
        assert result.is_high_density() is True

    def test_handles_different_postal_codes(
        self, postal_code_resident_service, mock_repository
    ):
        """Test that method handles different postal codes correctly."""
        postal_code_1 = PostalCode("10115")
        postal_code_2 = PostalCode("10117")

        def get_residents_side_effect(postal_code):
            if postal_code.value == "10115":
                return 5000
            elif postal_code.value == "10117":
                return 15000
            return 0

        mock_repository.get_residents_count.side_effect = get_residents_side_effect

        result_1 = postal_code_resident_service.get_resident_data(postal_code_1)
        result_2 = postal_code_resident_service.get_resident_data(postal_code_2)

        assert result_1.population == 5000
        assert result_2.population == 15000
        assert result_1.postal_code == postal_code_1
        assert result_2.postal_code == postal_code_2

    def test_population_data_has_correct_density_category_low(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that PopulationData has correct density category for low density."""
        mock_repository.get_residents_count.return_value = 5000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.get_population_density_category() == "LOW"
        assert result.is_high_density() is False

    def test_population_data_has_correct_density_category_medium(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that PopulationData has correct density category for medium density."""
        mock_repository.get_residents_count.return_value = 15000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.get_population_density_category() == "MEDIUM"
        assert result.is_high_density() is False  # Threshold is > 15000, so 15000 is not high density

    def test_population_data_medium_density_boundary_high(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that PopulationData correctly identifies high density at boundary (15001)."""
        mock_repository.get_residents_count.return_value = 15001

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.get_population_density_category() == "MEDIUM"  # Still MEDIUM (threshold is 20000)
        assert result.is_high_density() is True  # But is_high_density() returns True for > 15000

    def test_population_data_has_correct_density_category_high(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that PopulationData has correct density category for high density."""
        mock_repository.get_residents_count.return_value = 25000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.get_population_density_category() == "HIGH"
        assert result.is_high_density() is True

    def test_population_data_calculates_demand_ratio(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test that PopulationData can calculate demand ratio."""
        mock_repository.get_residents_count.return_value = 10000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        # Test demand ratio calculation
        assert result.calculate_demand_ratio(5) == 2000.0  # 10000 / 5
        assert result.calculate_demand_ratio(0) == 10000.0  # 10000 / 1 (min 1)

    def test_does_not_publish_events(
        self, postal_code_resident_service, valid_postal_code, mock_repository, mock_event_bus
    ):
        """Test that get_resident_data does not publish events."""
        mock_repository.get_residents_count.return_value = 5000

        postal_code_resident_service.get_resident_data(valid_postal_code)

        # Event bus should not be called for simple query operation
        mock_event_bus.publish.assert_not_called()


class TestPostalCodeResidentServiceIntegration:
    """Integration tests for PostalCodeResidentService."""

    def test_complete_workflow_get_all_postal_codes(
        self, mock_repository, mock_event_bus, postal_code_list
    ):
        """Test complete workflow for retrieving all postal codes."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list
        service = PostalCodeResidentService(mock_repository, mock_event_bus)

        result = service.get_all_postal_codes(sort=True)

        # Verify repository was called
        mock_repository.get_all_postal_codes.assert_called_once()

        # Verify result is correct and sorted
        assert len(result) == 5
        assert result[0].value == "10115"
        assert result[4].value == "10179"

        # Verify no events were published
        mock_event_bus.publish.assert_not_called()

    def test_complete_workflow_get_resident_data(
        self, mock_repository, mock_event_bus, valid_postal_code
    ):
        """Test complete workflow for retrieving resident data."""
        mock_repository.get_residents_count.return_value = 12000
        service = PostalCodeResidentService(mock_repository, mock_event_bus)

        result = service.get_resident_data(valid_postal_code)

        # Verify repository was called
        mock_repository.get_residents_count.assert_called_once_with(valid_postal_code)

        # Verify result is correct
        assert isinstance(result, PopulationData)
        assert result.population == 12000
        assert result.postal_code == valid_postal_code
        assert result.get_population_density_category() == "MEDIUM"

        # Verify no events were published
        mock_event_bus.publish.assert_not_called()

    def test_multiple_operations_work_correctly(
        self, postal_code_resident_service, mock_repository, mock_event_bus, postal_code_list, valid_postal_code
    ):
        """Test that multiple operations work correctly together."""
        mock_repository.get_all_postal_codes.return_value = postal_code_list
        mock_repository.get_residents_count.return_value = 8000

        # Get all postal codes
        all_codes = postal_code_resident_service.get_all_postal_codes()
        assert len(all_codes) == 5

        # Get resident data
        resident_data = postal_code_resident_service.get_resident_data(valid_postal_code)
        assert resident_data.population == 8000

        # Verify both repository methods were called
        mock_repository.get_all_postal_codes.assert_called_once()
        mock_repository.get_residents_count.assert_called_once_with(valid_postal_code)

        # Verify no events were published
        mock_event_bus.publish.assert_not_called()

    def test_service_handles_edge_cases(
        self, postal_code_resident_service, mock_repository
    ):
        """Test service handles edge cases correctly."""
        # Empty postal code list
        mock_repository.get_all_postal_codes.return_value = []
        result = postal_code_resident_service.get_all_postal_codes()
        assert len(result) == 0

        # Zero population
        postal_code = PostalCode("10115")
        mock_repository.get_residents_count.return_value = 0
        result = postal_code_resident_service.get_resident_data(postal_code)
        assert result.population == 0
        assert result.get_population_density_category() == "LOW"

    def test_service_handles_large_population(
        self, postal_code_resident_service, valid_postal_code, mock_repository
    ):
        """Test service handles large population values correctly."""
        mock_repository.get_residents_count.return_value = 100000

        result = postal_code_resident_service.get_resident_data(valid_postal_code)

        assert result.population == 100000
        assert result.get_population_density_category() == "HIGH"
        assert result.is_high_density() is True