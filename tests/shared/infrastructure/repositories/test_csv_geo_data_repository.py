import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.shared.infrastructure.repositories.CSVGeoDataRepository import CSVGeoDataRepository
from src.shared.domain.value_objects.PostalCode import PostalCode

class TestCSVGeoDataRepository(unittest.TestCase):
    """
    Unit tests for CSVGeoDataRepository.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.mock_file_path = "dummy_geo.csv"
        # Simulate raw data read from CSV
        self.raw_data = {
            "PLZ": [10115, 10247], # Usually read as ints by pandas
            "geometry": [
                "POLYGON((13.3 52.5, 13.4 52.5, 13.4 52.6, 13.3 52.6, 13.3 52.5))",
                "POLYGON((13.4 52.5, 13.5 52.5, 13.5 52.6, 13.4 52.6, 13.4 52.5))"
            ],
            "Other": ["Data", "Data"]
        }

    @patch("pandas.read_csv")
    def test_initialization_transform(self, mock_read_csv):
        """
        Test that initialization properly converts PLZ to string.
        """
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVGeoDataRepository(self.mock_file_path)

        # pylint: disable=protected-access
        self.assertEqual(repo._df["PLZ"].dtype, "object") # pandas object type for strings
        self.assertEqual(repo._df.iloc[0]["PLZ"], "10115")

    @patch("src.shared.infrastructure.repositories.CSVGeoDataRepository.GeoLocation")
    @patch("pandas.read_csv")
    def test_fetch_geolocation_data_found(self, mock_read_csv, mock_geo_location_cls):
        """
        Test fetching geolocation data for an existing postal code.
        """
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVGeoDataRepository(self.mock_file_path)
        
        mock_postal = MagicMock(spec=PostalCode)
        mock_postal.value = "10115"
        
        # Setup GeoLocation Mock return
        expected_geo_loc = MagicMock()
        mock_geo_location_cls.return_value = expected_geo_loc

        result = repo.fetch_geolocation_data(mock_postal)

        self.assertEqual(result, expected_geo_loc)
        
        mock_geo_location_cls.assert_called_once()
        call_args = mock_geo_location_cls.call_args[1]
        self.assertEqual(call_args['postal_code'], mock_postal)
        self.assertTrue("POLYGON" in str(call_args['boundary']))

    @patch("pandas.read_csv")
    def test_fetch_geolocation_data_not_found(self, mock_read_csv):
        """
        Test fetching geolocation returns None when postal code is not found.
        """
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVGeoDataRepository(self.mock_file_path)
        
        mock_postal = MagicMock(spec=PostalCode)
        mock_postal.value = "99999"

        result = repo.fetch_geolocation_data(mock_postal)

        self.assertIsNone(result)

    @patch("pandas.read_csv")
    def test_get_all_postal_codes(self, mock_read_csv):
        """
        Test retrieval of all unique postal codes.
        """
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVGeoDataRepository(self.mock_file_path)

        plz_list = repo.get_all_postal_codes()

        self.assertEqual(len(plz_list), 2)
        self.assertIn(10115, plz_list)
        self.assertIn(10247, plz_list)
        self.assertIsInstance(plz_list[0], int)

    @patch("pandas.read_csv")
    def test_get_all_postal_codes_error_handling(self, mock_read_csv):
        """
        Test that get_all_postal_codes handles missing columns gracefully.
        """
        # Data without PLZ column
        bad_data = {"col1": ["A"], "col2": ["B"]}
        mock_df = pd.DataFrame(bad_data)
        mock_read_csv.return_value = mock_df

        # We patch _transform because normally __init__ would crash if PLZ is missing.
        # By suppressing _transform, we can successfully create the repo object
        # and verify that get_all_postal_codes handles the missing column safely.
        with patch.object(CSVGeoDataRepository, '_transform'):
            repo = CSVGeoDataRepository(self.mock_file_path)
            plz_list = repo.get_all_postal_codes()

        self.assertEqual(plz_list, [])

if __name__ == '__main__':
    unittest.main()