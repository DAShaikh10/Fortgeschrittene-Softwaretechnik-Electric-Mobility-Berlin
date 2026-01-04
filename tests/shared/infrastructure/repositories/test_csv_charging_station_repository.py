"""Tests for CSV Charging Station Repository."""

# pylint: disable=redefined-outer-name

from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from src.shared.infrastructure.repositories.CSVChargingStationRepository import CSVChargingStationRepository
from src.shared.domain.entities.ChargingStation import ChargingStation
from src.shared.domain.value_objects.PostalCode import PostalCode


@pytest.fixture
def repo_setup():
    """
    Fixture to provide common setup data: raw CSV data and a dummy file path.
    """
    raw_data = {
        "Postleitzahl": ["10115", "10115", "12345"],
        "Bundesland": ["Berlin", "Berlin", "Berlin"],
        "Breitengrad": ["52,5323", "52,5324", "52,0000"],
        "Längengrad": ["13,3846", "13,3847", "13,0000"],
        "Nennleistung Ladeeinrichtung [kW]": ["22,0", "11,0", "50,0"],
        "OtherCol": ["Ignored", "Ignored", "Ignored"],
    }
    file_path = "dummy_path.csv"
    return raw_data, file_path


@patch("pandas.read_csv")
def test_initialization_and_transform(mock_read_csv, repo_setup):
    """
    Test that the repository initializes and transforms data correctly.
    """
    raw_data, file_path = repo_setup

    # Create a real DataFrame to be returned by the mock
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVChargingStationRepository(file_path)

    # Test through public interface - verify repository can load and query data
    # instead of checking internal dataframe state
    postal_code = PostalCode("10115")
    result = repo.find_stations_by_postal_code(postal_code)

    # If transformation worked correctly, we should be able to retrieve stations
    assert isinstance(result, list)

    # Verify read_csv was called with correct parameters (skiprows, etc.)
    mock_read_csv.assert_called_once()
    _, kwargs = mock_read_csv.call_args
    assert kwargs.get("skiprows") == 10
    assert kwargs.get("sep") == ";"


@patch("pandas.read_csv")
def test_find_stations_by_postal_code_found(mock_read_csv, repo_setup):
    """
    Test finding stations when they exist for a given postal code.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVChargingStationRepository(file_path)

    # Mock PostalCode
    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "10115"

    stations = repo.find_stations_by_postal_code(mock_postal)

    assert len(stations) == 2
    assert isinstance(stations[0], ChargingStation)

    # Verify attributes of the first station
    # Note: The order depends on DataFrame order, which is preserved here
    assert stations[0].latitude == 52.5323
    assert stations[0].longitude == 13.3846
    assert stations[0].power_capacity.kilowatts == 22.0
    assert stations[0].postal_code == mock_postal


@patch("pandas.read_csv")
def test_find_stations_by_postal_code_not_found(mock_read_csv, repo_setup):
    """
    Test finding stations returns empty list when none exist for postal code.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVChargingStationRepository(file_path)

    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "99999"  # Postal code not in data

    stations = repo.find_stations_by_postal_code(mock_postal)

    assert not stations


@patch("pandas.read_csv")
def test_get_dataframe_columns(mock_read_csv, repo_setup):
    """
    Test public inspection method get_dataframe_columns.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVChargingStationRepository(file_path)

    columns = repo.get_dataframe_columns()

    assert isinstance(columns, list)
    assert "PLZ" in columns
    assert "KW" in columns


@patch("pandas.read_csv")
def test_get_dataframe_value(mock_read_csv, repo_setup):
    """
    Test public inspection method get_dataframe_value.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVChargingStationRepository(file_path)

    value = repo.get_dataframe_value(0, "PLZ")

    assert value == "10115"
