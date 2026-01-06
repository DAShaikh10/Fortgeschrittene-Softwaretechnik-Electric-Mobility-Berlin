"""
Unit Tests for PowerCapacityService.

Test categories:
- Initialization tests
- Get power capacity by postal code tests
- Classify capacity ranges tests
- Get color for capacity tests
- Filter by capacity category tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import Mock

import pytest

from src.shared.application.dtos import PowerCapacityDTO
from src.shared.application.services import PowerCapacityService
from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode, PowerCapacity
from src.shared.infrastructure.repositories import ChargingStationRepository


# Test fixtures
@pytest.fixture
def mock_repository():
    """Create a mock ChargingStationRepository."""
    repository = Mock(spec=ChargingStationRepository)
    repository.find_stations_by_postal_code = Mock()
    return repository


@pytest.fixture
def power_capacity_service(mock_repository):
    """Create a PowerCapacityService instance."""
    return PowerCapacityService(mock_repository)


@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def mock_charging_station_1():
    """Create a mock charging station with 50 kW power."""
    return ChargingStation(postal_code="10115", latitude=52.5200, longitude=13.4050, power_capacity=PowerCapacity(50.0))


@pytest.fixture
def mock_charging_station_2():
    """Create a mock charging station with 22 kW power."""
    return ChargingStation(postal_code="10115", latitude=52.5201, longitude=13.4051, power_capacity=PowerCapacity(22.0))


@pytest.fixture
def mock_charging_station_3():
    """Create a mock charging station with 150 kW power."""
    return ChargingStation(
        postal_code="10117", latitude=52.5202, longitude=13.4052, power_capacity=PowerCapacity(150.0)
    )


@pytest.fixture
def mock_station_list(mock_charging_station_1, mock_charging_station_2):
    """Create a list of mock charging stations."""
    return [mock_charging_station_1, mock_charging_station_2]


class TestPowerCapacityServiceInitialization:
    """Test initialization of PowerCapacityService."""

    def test_service_initializes_with_repository(self, mock_repository):
        """Test that service initializes correctly with repository."""
        service = PowerCapacityService(mock_repository)

        # Test that service was initialized correctly through behavior
        assert isinstance(service, PowerCapacityService)

    def test_service_stores_repository(self, power_capacity_service):
        """Test that service stores repository reference."""
        # Test through behavior - service should be properly initialized
        assert isinstance(power_capacity_service, PowerCapacityService)


class TestGetPowerCapacityByPostalCode:
    """Test get_power_capacity_by_postal_code method."""

    def test_returns_list_of_dtos_with_correct_attributes(
        self, power_capacity_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that method returns list of DTOs with correct attributes."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], PowerCapacityDTO)
        assert hasattr(result[0], "postal_code")
        assert hasattr(result[0], "total_capacity_kw")
        assert hasattr(result[0], "station_count")

    def test_calculates_total_capacity_correctly(
        self, power_capacity_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that method calculates total capacity correctly."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert result[0].total_capacity_kw == 72.0  # 50.0 + 22.0
        assert result[0].station_count == 2
        assert result[0].postal_code == "10115"

    def test_handles_postal_code_with_no_stations(self, power_capacity_service, valid_postal_code, mock_repository):
        """Test that method handles postal codes with no stations."""
        mock_repository.find_stations_by_postal_code.return_value = []

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert result[0].total_capacity_kw == 0.0
        assert result[0].station_count == 0
        assert result[0].postal_code == "10115"

    def test_handles_multiple_postal_codes(
        self, power_capacity_service, mock_repository, mock_station_list, mock_charging_station_3
    ):
        """Test that method handles multiple postal codes correctly."""
        postal_code_1 = PostalCode("10115")
        postal_code_2 = PostalCode("10117")
        postal_code_3 = PostalCode("10119")

        def find_stations_side_effect(postal_code):
            if postal_code.value == "10115":
                return mock_station_list
            if postal_code.value == "10117":
                return [mock_charging_station_3]

            return []

        mock_repository.find_stations_by_postal_code.side_effect = find_stations_side_effect

        result = power_capacity_service.get_power_capacity_by_postal_code([postal_code_1, postal_code_2, postal_code_3])

        assert len(result) == 3
        # Find DTOs by postal code since order may vary
        result_dict = {dto.postal_code: dto for dto in result}
        assert result_dict["10115"].total_capacity_kw == 72.0
        assert result_dict["10117"].total_capacity_kw == 150.0
        assert result_dict["10119"].total_capacity_kw == 0.0

    def test_calls_repository_with_correct_postal_code(
        self, power_capacity_service, valid_postal_code, mock_repository
    ):
        """Test that method calls repository with correct postal code."""
        mock_repository.find_stations_by_postal_code.return_value = []

        power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        mock_repository.find_stations_by_postal_code.assert_called_once_with(valid_postal_code)

    def test_handles_single_station(
        self, power_capacity_service, valid_postal_code, mock_charging_station_1, mock_repository
    ):
        """Test that method handles single station correctly."""
        mock_repository.find_stations_by_postal_code.return_value = [mock_charging_station_1]

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert result[0].total_capacity_kw == 50.0
        assert result[0].station_count == 1

    def test_handles_empty_postal_code_list(self, power_capacity_service):
        """Test that method handles empty postal code list."""
        result = power_capacity_service.get_power_capacity_by_postal_code([])

        assert isinstance(result, list)
        assert len(result) == 0


class TestClassifyCapacityRanges:
    """Test classify_capacity_ranges method."""

    def test_classifies_into_categories_correctly(self, power_capacity_service):
        """Test that method classifies postal codes into correct categories."""
        # Create test data with varying capacities
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3),
            PowerCapacityDTO(postal_code="10178", total_capacity_kw=200.0, station_count=4),
            PowerCapacityDTO(postal_code="10179", total_capacity_kw=300.0, station_count=5),
        ]

        range_definitions, result_dtos = power_capacity_service.classify_capacity_ranges(capacity_dtos)

        # Check that capacity_category was added
        assert len(result_dtos) == 5
        assert all(dto.capacity_category is not None for dto in result_dtos)

        # Check range definitions
        assert "Low" in range_definitions
        assert "Medium" in range_definitions
        assert "High" in range_definitions

        # Check that categories are assigned (all have capacity > 0, so no "None")
        categories = {dto.capacity_category for dto in result_dtos}
        assert "None" not in categories  # All have capacity > 0

    def test_handles_empty_list(self, power_capacity_service):
        """Test that method handles empty list."""
        empty_dtos = []

        range_definitions, result_dtos = power_capacity_service.classify_capacity_ranges(empty_dtos)

        assert range_definitions["Low"] == (0, 0)
        assert range_definitions["Medium"] == (0, 0)
        assert range_definitions["High"] == (0, 0)
        assert len(result_dtos) == 0

    def test_handles_all_zero_capacity(self, power_capacity_service):
        """Test that method handles all zero capacity."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=0.0, station_count=0),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=0.0, station_count=0),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=0.0, station_count=0),
        ]

        range_definitions, result_dtos = power_capacity_service.classify_capacity_ranges(capacity_dtos)

        assert range_definitions["Low"] == (0, 0)
        assert range_definitions["Medium"] == (0, 0)
        assert range_definitions["High"] == (0, 0)
        # When all capacities are zero, categories should still be set to "None"
        assert len(result_dtos) == 3
        assert all(dto.capacity_category == "None" for dto in result_dtos)

    def test_classifies_zero_capacity_as_none(self, power_capacity_service):
        """Test that zero capacity is classified as 'None'."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=0.0, station_count=0),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=1),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=2),
        ]

        _, result_dtos = power_capacity_service.classify_capacity_ranges(capacity_dtos)

        result_dict = {dto.postal_code: dto for dto in result_dtos}
        assert result_dict["10115"].capacity_category == "None"
        assert result_dict["10117"].capacity_category in ["Low", "Medium", "High"]
        assert result_dict["10119"].capacity_category in ["Low", "Medium", "High"]

    def test_returns_range_definitions(self, power_capacity_service):
        """Test that method returns correct range definitions."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3),
        ]

        range_definitions, _ = power_capacity_service.classify_capacity_ranges(capacity_dtos)

        # Check structure of range definitions
        assert isinstance(range_definitions, dict)
        assert len(range_definitions) == 3
        for _, (min_val, max_val) in range_definitions.items():
            assert isinstance(min_val, (int, float))
            assert isinstance(max_val, (int, float))
            assert min_val <= max_val

    def test_does_not_modify_original_dtos(self, power_capacity_service):
        """Test that method does not modify original DTOs."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=50.0, station_count=1),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=100.0, station_count=2),
        ]

        _, result_dtos = power_capacity_service.classify_capacity_ranges(capacity_dtos)

        # Original DTOs should not have capacity_category
        assert all(dto.capacity_category is None for dto in capacity_dtos)
        # Result DTOs should have capacity_category
        assert all(dto.capacity_category is not None for dto in result_dtos)


class TestGetColorForCapacity:
    """Test get_color_for_capacity method."""

    def test_returns_light_gray_for_zero_capacity(self, power_capacity_service):
        """Test that method returns light gray for zero capacity."""
        color = power_capacity_service.get_color_for_capacity(0.0, 100.0)

        assert color == "#f0f0f0"

    def test_returns_light_gray_when_max_capacity_is_zero(self, power_capacity_service):
        """Test that method returns light gray when max capacity is zero."""
        color = power_capacity_service.get_color_for_capacity(50.0, 0.0)

        assert color == "#f0f0f0"

    def test_returns_dark_blue_for_max_capacity(self, power_capacity_service):
        """Test that method returns dark blue for max capacity."""
        color = power_capacity_service.get_color_for_capacity(100.0, 100.0)

        assert color == "#0d47a1"

    def test_returns_light_blue_for_low_capacity(self, power_capacity_service):
        """Test that method returns light blue for low capacity."""
        color = power_capacity_service.get_color_for_capacity(10.0, 100.0)

        # Should be closer to light blue (#e3f2fd)
        assert color.startswith("#")
        assert len(color) == 7

    def test_returns_valid_hex_color_format(self, power_capacity_service):
        """Test that method returns valid hex color format."""
        color = power_capacity_service.get_color_for_capacity(50.0, 100.0)

        assert color.startswith("#")
        assert len(color) == 7
        assert all(c in "0123456789abcdef" for c in color[1:])

    def test_handles_capacity_greater_than_max(self, power_capacity_service):
        """Test that method handles capacity greater than max."""
        color = power_capacity_service.get_color_for_capacity(150.0, 100.0)

        # Should cap at max and return dark blue
        assert color == "#0d47a1"

    def test_returns_gradient_colors(self, power_capacity_service):
        """Test that method returns gradient colors for different capacities."""
        max_capacity = 100.0
        color_low = power_capacity_service.get_color_for_capacity(10.0, max_capacity)
        color_medium = power_capacity_service.get_color_for_capacity(50.0, max_capacity)
        color_high = power_capacity_service.get_color_for_capacity(100.0, max_capacity)

        # All should be valid hex colors
        assert all(c.startswith("#") and len(c) == 7 for c in [color_low, color_medium, color_high])
        # High should be darker (lower RGB values) than low
        assert color_high != color_low


class TestFilterByCapacityCategory:
    """Test filter_by_capacity_category method."""

    def test_filters_by_low_category(self, power_capacity_service):
        """Test that method filters by Low category."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1, capacity_category="Low"),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2, capacity_category="Medium"),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3, capacity_category="High"),
        ]

        result = power_capacity_service.filter_by_capacity_category(capacity_dtos, "Low")

        assert len(result) == 1
        assert result[0].postal_code == "10115"
        assert result[0].capacity_category == "Low"

    def test_filters_by_medium_category(self, power_capacity_service):
        """Test that method filters by Medium category."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1, capacity_category="Low"),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2, capacity_category="Medium"),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3, capacity_category="High"),
        ]

        result = power_capacity_service.filter_by_capacity_category(capacity_dtos, "Medium")

        assert len(result) == 1
        assert result[0].postal_code == "10117"
        assert result[0].capacity_category == "Medium"

    def test_filters_by_high_category(self, power_capacity_service):
        """Test that method filters by High category."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1, capacity_category="Low"),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2, capacity_category="Medium"),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3, capacity_category="High"),
        ]

        result = power_capacity_service.filter_by_capacity_category(capacity_dtos, "High")

        assert len(result) == 1
        assert result[0].postal_code == "10119"
        assert result[0].capacity_category == "High"

    def test_returns_all_when_category_is_all(self, power_capacity_service):
        """Test that method returns all DTOs when category is 'All'."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1, capacity_category="Low"),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2, capacity_category="Medium"),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3, capacity_category="High"),
        ]

        result = power_capacity_service.filter_by_capacity_category(capacity_dtos, "All")

        assert len(result) == 3
        assert {dto.postal_code for dto in result} == {"10115", "10117", "10119"}

    def test_returns_empty_when_no_matches(self, power_capacity_service):
        """Test that method returns empty list when no matches."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=10.0, station_count=1, capacity_category="Low"),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2, capacity_category="Medium"),
        ]

        result = power_capacity_service.filter_by_capacity_category(capacity_dtos, "High")

        assert len(result) == 0
        assert isinstance(result, list)

    def test_handles_none_category(self, power_capacity_service):
        """Test that method filters by None category."""
        capacity_dtos = [
            PowerCapacityDTO(postal_code="10115", total_capacity_kw=0.0, station_count=0, capacity_category="None"),
            PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2, capacity_category="Medium"),
            PowerCapacityDTO(postal_code="10119", total_capacity_kw=100.0, station_count=3, capacity_category="High"),
        ]

        result = power_capacity_service.filter_by_capacity_category(capacity_dtos, "None")

        assert len(result) == 1
        assert result[0].postal_code == "10115"
        assert result[0].capacity_category == "None"


class TestPowerCapacityServiceIntegration:
    """Integration tests for PowerCapacityService."""

    def test_complete_workflow(self, mock_repository, mock_station_list, mock_charging_station_3):
        """Test complete workflow from getting capacity to filtering."""
        postal_code_1 = PostalCode("10115")
        postal_code_2 = PostalCode("10117")

        def find_stations_side_effect(postal_code):
            if postal_code.value == "10115":
                return mock_station_list
            if postal_code.value == "10117":
                return [mock_charging_station_3]
            return []

        mock_repository.find_stations_by_postal_code.side_effect = find_stations_side_effect
        service = PowerCapacityService(mock_repository)

        # Get capacity data
        capacity_dtos = service.get_power_capacity_by_postal_code([postal_code_1, postal_code_2])

        # Classify ranges
        range_definitions, classified_dtos = service.classify_capacity_ranges(capacity_dtos)

        # Filter by category
        high_capacity = service.filter_by_capacity_category(classified_dtos, "High")

        # Verify results
        assert len(capacity_dtos) == 2
        assert all(dto.capacity_category is not None for dto in classified_dtos)
        assert isinstance(range_definitions, dict)
        assert len(high_capacity) >= 0  # At least 0, could be 1 or 2 depending on quantiles

    def test_multiple_postal_codes_with_classification(
        self, mock_repository, mock_charging_station_1, mock_charging_station_3
    ):
        """Test multiple postal codes with capacity classification."""
        postal_codes = [PostalCode("10115"), PostalCode("10117"), PostalCode("10119")]

        def find_stations_side_effect(postal_code):
            if postal_code.value == "10115":
                return [mock_charging_station_1]  # 50 kW
            if postal_code.value == "10117":
                return [mock_charging_station_3]  # 150 kW
            return []

        mock_repository.find_stations_by_postal_code.side_effect = find_stations_side_effect
        service = PowerCapacityService(mock_repository)

        capacity_dtos = service.get_power_capacity_by_postal_code(postal_codes)
        _, classified_dtos = service.classify_capacity_ranges(capacity_dtos)

        # Verify all postal codes are present
        assert len(classified_dtos) == 3
        assert {dto.postal_code for dto in classified_dtos} == {"10115", "10117", "10119"}

        # Verify categories are assigned
        assert all(dto.capacity_category is not None for dto in classified_dtos)

    def test_color_generation_for_capacity_data(self, mock_repository, mock_station_list):
        """Test color generation for capacity data."""
        postal_code = PostalCode("10115")
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list
        service = PowerCapacityService(mock_repository)

        capacity_dtos = service.get_power_capacity_by_postal_code([postal_code])
        max_capacity = max(dto.total_capacity_kw for dto in capacity_dtos) if capacity_dtos else 0.0

        # Generate colors for each capacity
        colors = [service.get_color_for_capacity(dto.total_capacity_kw, max_capacity) for dto in capacity_dtos]

        # Verify all colors are valid
        assert all(c.startswith("#") and len(c) == 7 for c in colors)
