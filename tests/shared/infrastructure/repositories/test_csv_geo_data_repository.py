"""Tests for CSV Geo Data Repository."""

# pylint: disable=redefined-outer-name

from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from shapely.geometry import Polygon

from src.shared.infrastructure.geospatial import GeopandasBoundary
from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.repositories import CSVGeoDataRepository


@pytest.fixture
def repo_setup():
    """
    Fixture to provide common setup data: raw CSV data and a dummy file path.
    """
    raw_data = {
        "PLZ": [10115, 10247],  # Usually read as ints by pandas
        "geometry": [
            "POLYGON((13.3 52.5, 13.4 52.5, 13.4 52.6, 13.3 52.6, 13.3 52.5))",
            "POLYGON((13.4 52.5, 13.5 52.5, 13.5 52.6, 13.4 52.6, 13.4 52.5))",
        ],
        "Other": ["Data", "Data"],
    }
    file_path = "dummy_geo.csv"
    return raw_data, file_path


@patch("pandas.read_csv")
def test_initialization_transform(mock_read_csv, repo_setup):
    """
    Test that initialization properly converts PLZ to string.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    # Test through public interface - try to fetch data
    # The internal transformation should be transparent
    postal_code = PostalCode("10115")
    result = repo.fetch_geolocation_data(postal_code)
    # If transformation worked, data should be retrievable
    assert result is not None


@patch("src.shared.infrastructure.repositories.csv_geo_data_repository.GeoLocation")
@patch("src.shared.infrastructure.repositories.csv_geo_data_repository.CSVGeoDataRepository._coerce_boundary")
@patch("pandas.read_csv")
def test_fetch_geolocation_data_found(mock_read_csv, mock_coerce, mock_geo_location_cls, repo_setup):
    """
    Test fetching geolocation data for an existing postal code.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "10115"

    boundary_sentinel = object()
    mock_coerce.return_value = boundary_sentinel

    # Setup GeoLocation Mock return
    expected_geo_loc = MagicMock()
    mock_geo_location_cls.return_value = expected_geo_loc

    result = repo.fetch_geolocation_data(mock_postal)

    assert result == expected_geo_loc

    mock_geo_location_cls.assert_called_once()
    call_args = mock_geo_location_cls.call_args[1]
    assert call_args["postal_code"] == mock_postal
    assert call_args["boundary"] is boundary_sentinel
    mock_coerce.assert_called_once()


@patch("pandas.read_csv")
def test_fetch_geolocation_data_not_found(mock_read_csv, repo_setup):
    """
    Test fetching geolocation returns None when postal code is not found.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "99999"

    result = repo.fetch_geolocation_data(mock_postal)

    assert result is None


@patch("pandas.read_csv")
def test_get_all_postal_codes(mock_read_csv, repo_setup):
    """
    Test retrieval of all unique postal codes.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    plz_list = repo.get_all_postal_codes()

    assert len(plz_list) == 2
    assert 10115 in plz_list
    assert 10247 in plz_list
    assert isinstance(plz_list[0], int)


@patch("pandas.read_csv")
def test_get_all_postal_codes_error_handling(mock_read_csv, repo_setup):
    """
    Test that get_all_postal_codes handles missing columns gracefully.
    """
    _, file_path = repo_setup
    # Data without PLZ column
    bad_data = {"col1": ["A"], "col2": ["B"]}
    mock_df = pd.DataFrame(bad_data)
    mock_read_csv.return_value = mock_df

    # We patch _transform because normally __init__ would crash if PLZ is missing.
    # By suppressing _transform, we can successfully create the repo object
    # and verify that get_all_postal_codes handles the missing column safely.
    with patch.object(CSVGeoDataRepository, "_transform"):
        repo = CSVGeoDataRepository(file_path)
        plz_list = repo.get_all_postal_codes()

    assert plz_list == []


def test_coerce_boundary_returns_existing_boundary():
    """Test that coerce_boundary returns the input if it's already a GeopandasBoundary."""
    repo = CSVGeoDataRepository.__new__(CSVGeoDataRepository)  # bypass __init__
    boundary = MagicMock(spec=GeopandasBoundary)

    result = repo.coerce_boundary(boundary)

    assert result is boundary


def test_coerce_boundary_builds_from_wkt():
    """Test that coerce_boundary builds a GeopandasBoundary from WKT string."""
    repo = CSVGeoDataRepository.__new__(CSVGeoDataRepository)  # bypass __init__
    sentinel = object()
    with patch(
        "src.shared.infrastructure.repositories.csv_geo_data_repository.GeopandasBoundary.from_wkt",
        return_value=sentinel,
    ) as mock_from_wkt:
        result = repo.coerce_boundary("POLYGON((13 52, 13 53, 14 53, 13 52))")

    assert result is sentinel
    mock_from_wkt.assert_called_once()


def test_coerce_boundary_wraps_geodataframe():
    """Test that coerce_boundary wraps a Polygon in a GeopandasBoundary."""
    repo = CSVGeoDataRepository.__new__(CSVGeoDataRepository)  # bypass __init__
    polygon = Polygon([(13.4, 52.5), (13.5, 52.5), (13.5, 52.6), (13.4, 52.6), (13.4, 52.5)])

    result = repo.coerce_boundary(polygon)

    assert isinstance(result, GeopandasBoundary)
    assert not result.is_empty()
    assert hasattr(result, "geometry")


@patch("pandas.read_csv")
def test_get_all_postal_codes_exception_handling(mock_read_csv, repo_setup):
    """
    Test that get_all_postal_codes handles exceptions during conversion gracefully.
    """
    _, file_path = repo_setup
    # Create a DataFrame where astype(int) will fail
    bad_data = {"PLZ": ["invalid", "data"]}
    mock_df = pd.DataFrame(bad_data)
    mock_read_csv.return_value = mock_df

    with patch.object(CSVGeoDataRepository, "_transform"):
        repo = CSVGeoDataRepository(file_path)
        # This should catch the exception and return []
        plz_list = repo.get_all_postal_codes()

    assert plz_list == []


@patch("pandas.read_csv")
def test_get_dataframe_columns(mock_read_csv, repo_setup):
    """
    Test public inspection method get_dataframe_columns.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    columns = repo.get_dataframe_columns()

    assert isinstance(columns, list)
    assert "PLZ" in columns
    assert "geometry" in columns


@patch("pandas.read_csv")
def test_get_dataframe_column_dtype(mock_read_csv, repo_setup):
    """
    Test public inspection method get_dataframe_column_dtype.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    dtype = repo.get_dataframe_column_dtype("PLZ")

    assert isinstance(dtype, str)
    assert "object" in dtype  # PLZ is converted to string type


@patch("pandas.read_csv")
def test_get_dataframe_value(mock_read_csv, repo_setup):
    """
    Test public inspection method get_dataframe_value.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)

    value = repo.get_dataframe_value(0, "PLZ")

    assert value == "10115"
