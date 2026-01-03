"""
Shared Infrastructure CSVPopulationRepository Tests.
"""

# pylint: disable=redefined-outer-name

from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from src.shared.infrastructure.repositories.CSVPopulationRepository import CSVPopulationRepository
from src.shared.domain.value_objects.PostalCode import PostalCode


@pytest.fixture
def population_data_setup():
    """
    Fixture to provide raw CSV data and file path for testing.
    Includes edge cases like commas in coordinates and duplicate PLZs to test aggregation.
    """
    raw_data = {
        "plz": ["10115", "10115", "10247", "99999"],
        "einwohner": [500, 300, 15000, 100],
        "lat": ["52,5323", "52,5323", "52,0000", "0,0"],
        "lon": ["13,3846", "13,3846", "13,0000", "0,0"],
        "other_col": ["ignore", "ignore", "ignore", "ignore"],
    }
    file_path = "dummy_population.csv"
    return raw_data, file_path


@patch("pandas.read_csv")
def test_initialization_and_transform(mock_read_csv, population_data_setup):
    """
    Test that the repository initializes and transforms data correctly.
    Verifies column type conversion and decimal separator replacement.
    """
    raw_data, file_path = population_data_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVPopulationRepository(file_path)

    # pylint: disable=protected-access
    # Check if 'plz' is string
    assert repo._df["plz"].dtype == "object"

    # Check if coordinates replaced ',' with '.'
    assert repo._df.iloc[0]["lat"] == "52.5323"
    assert repo._df.iloc[0]["lon"] == "13.3846"

    # Verify read_csv parameters
    mock_read_csv.assert_called_once()
    _, kwargs = mock_read_csv.call_args
    assert kwargs.get("sep") == ","


@patch("src.shared.infrastructure.repositories.CSVPopulationRepository.PostalCode")
@patch("pandas.read_csv")
def test_get_all_postal_codes_success(mock_read_csv, mock_postal_code_cls, population_data_setup):
    """
    Test retrieving all unique postal codes as PostalCode objects.
    """
    raw_data, file_path = population_data_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVPopulationRepository(file_path)

    # Mock successful creation of PostalCode objects
    mock_instance = MagicMock()
    mock_postal_code_cls.return_value = mock_instance

    result = repo.get_all_postal_codes()

    # The dataset has 3 unique PLZs: 10115, 10247, 99999
    # (10115 appears twice, but unique() filters it)
    assert len(result) == 3
    assert all(res == mock_instance for res in result)

    # Verify PostalCode was instantiated with the string values
    assert mock_postal_code_cls.call_count == 3
    # Check that it was called with '10115' at least once
    call_args_list = [args[0][0] for args in mock_postal_code_cls.call_args_list]
    assert "10115" in call_args_list
    assert "10247" in call_args_list


@patch("src.shared.infrastructure.repositories.CSVPopulationRepository.PostalCode")
@patch("pandas.read_csv")
def test_get_all_postal_codes_skip_invalid(mock_read_csv, mock_postal_code_cls, population_data_setup):
    """
    Test that invalid postal codes (raising ValueError) are skipped gracefully.
    """
    raw_data, file_path = population_data_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVPopulationRepository(file_path)

    # Side effect: First call succeeds, second fails, third succeeds
    def side_effect(plz):
        if plz == "99999":
            raise ValueError("Invalid PLZ")
        return MagicMock(spec=PostalCode)

    mock_postal_code_cls.side_effect = side_effect

    result = repo.get_all_postal_codes()

    # Should contain 10115 and 10247, but skip 99999
    assert len(result) == 2


@patch("pandas.read_csv")
def test_get_residents_count_found(mock_read_csv, population_data_setup):
    """
    Test getting resident count for a specific postal code.
    Should sum up values if multiple entries exist for the same PLZ.
    """
    raw_data, file_path = population_data_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVPopulationRepository(file_path)

    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "10115"

    # In setup: 10115 has two entries: 500 and 300. Sum should be 800.
    count = repo.get_residents_count(mock_postal)
    assert count == 800
    assert isinstance(count, int)


@patch("pandas.read_csv")
def test_get_residents_count_not_found(mock_read_csv, population_data_setup):
    """
    Test that asking for a non-existent postal code returns 0.
    """
    raw_data, file_path = population_data_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVPopulationRepository(file_path)

    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "00000"  # Not in dataset

    count = repo.get_residents_count(mock_postal)
    assert count == 0
