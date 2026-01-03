import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.shared.infrastructure.repositories.CSVGeoDataRepository import CSVGeoDataRepository
from src.shared.domain.value_objects.PostalCode import PostalCode

@pytest.fixture
def repo_setup():
    """
    Fixture to provide common setup data: raw CSV data and a dummy file path.
    """
    raw_data = {
        "PLZ": [10115, 10247], # Usually read as ints by pandas
        "geometry": [
            "POLYGON((13.3 52.5, 13.4 52.5, 13.4 52.6, 13.3 52.6, 13.3 52.5))",
            "POLYGON((13.4 52.5, 13.5 52.5, 13.5 52.6, 13.4 52.6, 13.4 52.5))"
        ],
        "Other": ["Data", "Data"]
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

    # pylint: disable=protected-access
    assert repo._df["PLZ"].dtype == "object" # pandas object type for strings
    assert repo._df.iloc[0]["PLZ"] == "10115"

@patch("src.shared.infrastructure.repositories.CSVGeoDataRepository.GeoLocation")
@patch("pandas.read_csv")
def test_fetch_geolocation_data_found(mock_read_csv, mock_geo_location_cls, repo_setup):
    """
    Test fetching geolocation data for an existing postal code.
    """
    raw_data, file_path = repo_setup
    mock_df = pd.DataFrame(raw_data)
    mock_read_csv.return_value = mock_df

    repo = CSVGeoDataRepository(file_path)
    
    mock_postal = MagicMock(spec=PostalCode)
    mock_postal.value = "10115"
    
    # Setup GeoLocation Mock return
    expected_geo_loc = MagicMock()
    mock_geo_location_cls.return_value = expected_geo_loc

    result = repo.fetch_geolocation_data(mock_postal)

    assert result == expected_geo_loc
    
    mock_geo_location_cls.assert_called_once()
    call_args = mock_geo_location_cls.call_args[1]
    assert call_args['postal_code'] == mock_postal
    assert "POLYGON" in str(call_args['boundary'])

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
    with patch.object(CSVGeoDataRepository, '_transform'):
        repo = CSVGeoDataRepository(file_path)
        plz_list = repo.get_all_postal_codes()

    assert plz_list == []