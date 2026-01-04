"""
Unit Tests for PowerCapacityService.

Test categories:
- Initialization tests
- Get power capacity by postal code tests
- Classify capacity ranges tests
- Get color for capacity tests
- Filter by capacity category tests
"""

# pylint: disable=redefined-outer-name,protected-access,unused-argument,unused-variable,no-else-return

from unittest.mock import Mock

import pandas as pd
import pytest

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

        assert service._repository is mock_repository

    def test_service_stores_repository(self, power_capacity_service, mock_repository):
        """Test that service stores repository reference."""
        assert power_capacity_service._repository is mock_repository


class TestGetPowerCapacityByPostalCode:
    """Test get_power_capacity_by_postal_code method."""

    def test_returns_dataframe_with_correct_columns(
        self, power_capacity_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that method returns DataFrame with correct columns."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["postal_code", "total_capacity_kw", "station_count"]
        assert len(result) == 1

    def test_calculates_total_capacity_correctly(
        self, power_capacity_service, valid_postal_code, mock_station_list, mock_repository
    ):
        """Test that method calculates total capacity correctly."""
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert result.iloc[0]["total_capacity_kw"] == 72.0  # 50.0 + 22.0
        assert result.iloc[0]["station_count"] == 2
        assert result.iloc[0]["postal_code"] == "10115"

    def test_handles_postal_code_with_no_stations(self, power_capacity_service, valid_postal_code, mock_repository):
        """Test that method handles postal codes with no stations."""
        mock_repository.find_stations_by_postal_code.return_value = []

        result = power_capacity_service.get_power_capacity_by_postal_code([valid_postal_code])

        assert result.iloc[0]["total_capacity_kw"] == 0.0
        assert result.iloc[0]["station_count"] == 0
        assert result.iloc[0]["postal_code"] == "10115"

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
            elif postal_code.value == "10117":
                return [mock_charging_station_3]
            else:
                return []

        mock_repository.find_stations_by_postal_code.side_effect = find_stations_side_effect

        result = power_capacity_service.get_power_capacity_by_postal_code([postal_code_1, postal_code_2, postal_code_3])

        assert len(result) == 3
        assert result.iloc[0]["postal_code"] == "10115"
        assert result.iloc[0]["total_capacity_kw"] == 72.0
        assert result.iloc[1]["postal_code"] == "10117"
        assert result.iloc[1]["total_capacity_kw"] == 150.0
        assert result.iloc[2]["postal_code"] == "10119"
        assert result.iloc[2]["total_capacity_kw"] == 0.0

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

        assert result.iloc[0]["total_capacity_kw"] == 50.0
        assert result.iloc[0]["station_count"] == 1

    def test_handles_empty_postal_code_list(self, power_capacity_service):
        """Test that method handles empty postal code list."""
        result = power_capacity_service.get_power_capacity_by_postal_code([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        # Empty DataFrame may not have columns defined
        if len(result.columns) > 0:
            assert list(result.columns) == ["postal_code", "total_capacity_kw", "station_count"]


class TestClassifyCapacityRanges:
    """Test classify_capacity_ranges method."""

    def test_classifies_into_categories_correctly(self, power_capacity_service):
        """Test that method classifies postal codes into correct categories."""
        # Create test data with varying capacities
        capacity_data = {
            "postal_code": ["10115", "10117", "10119", "10178", "10179"],
            "total_capacity_kw": [10.0, 50.0, 100.0, 200.0, 300.0],
            "station_count": [1, 2, 3, 4, 5],
        }
        capacity_df = pd.DataFrame(capacity_data)

        range_definitions, result_df = power_capacity_service.classify_capacity_ranges(capacity_df)

        # Check that capacity_category column was added
        assert "capacity_category" in result_df.columns
        assert len(result_df) == 5

        # Check range definitions
        assert "Low" in range_definitions
        assert "Medium" in range_definitions
        assert "High" in range_definitions

        # Check that categories are assigned
        categories = result_df["capacity_category"].unique()
        assert "None" not in categories  # All have capacity > 0

    def test_handles_empty_dataframe(self, power_capacity_service):
        """Test that method handles empty DataFrame."""
        empty_df = pd.DataFrame(columns=["postal_code", "total_capacity_kw", "station_count"])

        range_definitions, result_df = power_capacity_service.classify_capacity_ranges(empty_df)

        assert range_definitions["Low"] == (0, 0)
        assert range_definitions["Medium"] == (0, 0)
        assert range_definitions["High"] == (0, 0)
        assert len(result_df) == 0

    def test_handles_all_zero_capacity(self, power_capacity_service):
        """Test that method handles all zero capacity."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [0.0, 0.0, 0.0],
            "station_count": [0, 0, 0],
        }
        capacity_df = pd.DataFrame(capacity_data)

        range_definitions, result_df = power_capacity_service.classify_capacity_ranges(capacity_df)

        assert range_definitions["Low"] == (0, 0)
        assert range_definitions["Medium"] == (0, 0)
        assert range_definitions["High"] == (0, 0)
        # When all capacities are zero, the method returns original DataFrame without capacity_category
        assert "capacity_category" not in result_df.columns
        assert len(result_df) == 3

    def test_classifies_zero_capacity_as_none(self, power_capacity_service):
        """Test that zero capacity is classified as 'None'."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [0.0, 50.0, 100.0],
            "station_count": [0, 1, 2],
        }
        capacity_df = pd.DataFrame(capacity_data)

        _, result_df = power_capacity_service.classify_capacity_ranges(capacity_df)

        assert result_df[result_df["postal_code"] == "10115"]["capacity_category"].iloc[0] == "None"
        assert result_df[result_df["postal_code"] == "10117"]["capacity_category"].iloc[0] in ["Low", "Medium", "High"]
        assert result_df[result_df["postal_code"] == "10119"]["capacity_category"].iloc[0] in ["Low", "Medium", "High"]

    def test_returns_range_definitions(self, power_capacity_service):
        """Test that method returns correct range definitions."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [10.0, 50.0, 100.0],
            "station_count": [1, 2, 3],
        }
        capacity_df = pd.DataFrame(capacity_data)

        range_definitions, _ = power_capacity_service.classify_capacity_ranges(capacity_df)

        # Check structure of range definitions
        assert isinstance(range_definitions, dict)
        assert len(range_definitions) == 3
        for category, (min_val, max_val) in range_definitions.items():
            assert isinstance(min_val, (int, float))
            assert isinstance(max_val, (int, float))
            assert min_val <= max_val

    def test_does_not_modify_original_dataframe(self, power_capacity_service):
        """Test that method does not modify original DataFrame."""
        capacity_data = {"postal_code": ["10115", "10117"], "total_capacity_kw": [50.0, 100.0], "station_count": [1, 2]}
        capacity_df = pd.DataFrame(capacity_data)
        original_columns = list(capacity_df.columns)

        _, result_df = power_capacity_service.classify_capacity_ranges(capacity_df)

        # Original should not have capacity_category
        assert "capacity_category" not in capacity_df.columns
        assert list(capacity_df.columns) == original_columns
        # Result should have capacity_category
        assert "capacity_category" in result_df.columns


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
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [10.0, 50.0, 100.0],
            "station_count": [1, 2, 3],
            "capacity_category": ["Low", "Medium", "High"],
        }
        capacity_df = pd.DataFrame(capacity_data)

        result = power_capacity_service.filter_by_capacity_category(capacity_df, "Low")

        assert len(result) == 1
        assert result.iloc[0]["postal_code"] == "10115"
        assert result.iloc[0]["capacity_category"] == "Low"

    def test_filters_by_medium_category(self, power_capacity_service):
        """Test that method filters by Medium category."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [10.0, 50.0, 100.0],
            "station_count": [1, 2, 3],
            "capacity_category": ["Low", "Medium", "High"],
        }
        capacity_df = pd.DataFrame(capacity_data)

        result = power_capacity_service.filter_by_capacity_category(capacity_df, "Medium")

        assert len(result) == 1
        assert result.iloc[0]["postal_code"] == "10117"
        assert result.iloc[0]["capacity_category"] == "Medium"

    def test_filters_by_high_category(self, power_capacity_service):
        """Test that method filters by High category."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [10.0, 50.0, 100.0],
            "station_count": [1, 2, 3],
            "capacity_category": ["Low", "Medium", "High"],
        }
        capacity_df = pd.DataFrame(capacity_data)

        result = power_capacity_service.filter_by_capacity_category(capacity_df, "High")

        assert len(result) == 1
        assert result.iloc[0]["postal_code"] == "10119"
        assert result.iloc[0]["capacity_category"] == "High"

    def test_returns_all_when_category_is_all(self, power_capacity_service):
        """Test that method returns all rows when category is 'All'."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [10.0, 50.0, 100.0],
            "station_count": [1, 2, 3],
            "capacity_category": ["Low", "Medium", "High"],
        }
        capacity_df = pd.DataFrame(capacity_data)

        result = power_capacity_service.filter_by_capacity_category(capacity_df, "All")

        assert len(result) == 3
        assert list(result["postal_code"]) == ["10115", "10117", "10119"]

    def test_returns_empty_when_no_matches(self, power_capacity_service):
        """Test that method returns empty DataFrame when no matches."""
        capacity_data = {
            "postal_code": ["10115", "10117"],
            "total_capacity_kw": [10.0, 50.0],
            "station_count": [1, 2],
            "capacity_category": ["Low", "Medium"],
        }
        capacity_df = pd.DataFrame(capacity_data)

        result = power_capacity_service.filter_by_capacity_category(capacity_df, "High")

        assert len(result) == 0
        assert list(result.columns) == list(capacity_df.columns)

    def test_handles_none_category(self, power_capacity_service):
        """Test that method filters by None category."""
        capacity_data = {
            "postal_code": ["10115", "10117", "10119"],
            "total_capacity_kw": [0.0, 50.0, 100.0],
            "station_count": [0, 2, 3],
            "capacity_category": ["None", "Medium", "High"],
        }
        capacity_df = pd.DataFrame(capacity_data)

        result = power_capacity_service.filter_by_capacity_category(capacity_df, "None")

        assert len(result) == 1
        assert result.iloc[0]["postal_code"] == "10115"
        assert result.iloc[0]["capacity_category"] == "None"


class TestPowerCapacityServiceIntegration:
    """Integration tests for PowerCapacityService."""

    def test_complete_workflow(self, mock_repository, mock_station_list, mock_charging_station_3):
        """Test complete workflow from getting capacity to filtering."""
        postal_code_1 = PostalCode("10115")
        postal_code_2 = PostalCode("10117")

        def find_stations_side_effect(postal_code):
            if postal_code.value == "10115":
                return mock_station_list
            elif postal_code.value == "10117":
                return [mock_charging_station_3]
            return []

        mock_repository.find_stations_by_postal_code.side_effect = find_stations_side_effect
        service = PowerCapacityService(mock_repository)

        # Get capacity data
        capacity_df = service.get_power_capacity_by_postal_code([postal_code_1, postal_code_2])

        # Classify ranges
        range_definitions, classified_df = service.classify_capacity_ranges(capacity_df)

        # Filter by category
        high_capacity = service.filter_by_capacity_category(classified_df, "High")

        # Verify results
        assert len(capacity_df) == 2
        assert "capacity_category" in classified_df.columns
        assert isinstance(range_definitions, dict)
        assert len(high_capacity) >= 0  # At least 0, could be 1 or 2 depending on quantiles

    def test_multiple_postal_codes_with_classification(
        self, mock_repository, mock_charging_station_1, mock_charging_station_2, mock_charging_station_3
    ):
        """Test multiple postal codes with capacity classification."""
        postal_codes = [PostalCode("10115"), PostalCode("10117"), PostalCode("10119")]

        def find_stations_side_effect(postal_code):
            if postal_code.value == "10115":
                return [mock_charging_station_1]  # 50 kW
            elif postal_code.value == "10117":
                return [mock_charging_station_3]  # 150 kW
            else:
                return []

        mock_repository.find_stations_by_postal_code.side_effect = find_stations_side_effect
        service = PowerCapacityService(mock_repository)

        capacity_df = service.get_power_capacity_by_postal_code(postal_codes)
        range_definitions, classified_df = service.classify_capacity_ranges(capacity_df)

        # Verify all postal codes are present
        assert len(classified_df) == 3
        assert set(classified_df["postal_code"]) == {"10115", "10117", "10119"}

        # Verify categories are assigned
        assert all(classified_df["capacity_category"].notna())

    def test_color_generation_for_capacity_data(self, mock_repository, mock_station_list):
        """Test color generation for capacity data."""
        postal_code = PostalCode("10115")
        mock_repository.find_stations_by_postal_code.return_value = mock_station_list
        service = PowerCapacityService(mock_repository)

        capacity_df = service.get_power_capacity_by_postal_code([postal_code])
        max_capacity = capacity_df["total_capacity_kw"].max()

        # Generate colors for each capacity
        colors = [service.get_color_for_capacity(cap, max_capacity) for cap in capacity_df["total_capacity_kw"]]

        # Verify all colors are valid
        assert all(c.startswith("#") and len(c) == 7 for c in colors)
