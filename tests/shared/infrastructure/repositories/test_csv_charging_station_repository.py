import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

from src.shared.infrastructure.repositories.CSVChargingStationRepository import CSVChargingStationRepository
from src.shared.domain.entities.ChargingStation import ChargingStation
from src.shared.domain.value_objects.PostalCode import PostalCode

class TestCSVChargingStationRepository(unittest.TestCase):
    """
    Unit tests for CSVChargingStationRepository.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.mock_file_path = "dummy_path.csv"
        
        # Create a dictionary representing the data AFTER loading the CSV
        # Note: We simulate the state of data as if read_csv just ran.
        # Decimals are still commas here because that's how they are in the raw CSV 
        # before the repository's _transform method processes them.
        self.raw_data = {
            "Postleitzahl": ["10115", "10115", "12345"],
            "Bundesland": ["Berlin", "Berlin", "Berlin"],
            "Breitengrad": ["52,5323", "52,5324", "52,0000"],
            "Längengrad": ["13,3846", "13,3847", "13,0000"],
            "Nennleistung Ladeeinrichtung [kW]": ["22,0", "11,0", "50,0"],
            "OtherCol": ["Ignored", "Ignored", "Ignored"]
        }

    @patch("pandas.read_csv")
    def test_initialization_and_transform(self, mock_read_csv):
        """
        Test that the repository initializes and transforms data correctly.
        """
        # Create a real DataFrame to be returned by the mock
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVChargingStationRepository(self.mock_file_path)

        # Access the internal dataframe to verify transformation
        # pylint: disable=protected-access
        self.assertTrue("PLZ" in repo._df.columns)
        self.assertTrue("KW" in repo._df.columns)
        self.assertTrue("Breitengrad" in repo._df.columns)
        
        # Check if columns were renamed and values transformed (commas to dots)
        self.assertEqual(repo._df.iloc[0]["Breitengrad"], "52.5323")
        self.assertEqual(repo._df.iloc[0]["KW"], "22.0")
        
        # Verify read_csv was called with correct parameters (skiprows, etc.)
        mock_read_csv.assert_called_once()
        _, kwargs = mock_read_csv.call_args
        self.assertEqual(kwargs.get("skiprows"), 10)
        self.assertEqual(kwargs.get("sep"), ";")

    @patch("pandas.read_csv")
    def test_find_stations_by_postal_code_found(self, mock_read_csv):
        """
        Test finding stations when they exist for a given postal code.
        """
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVChargingStationRepository(self.mock_file_path)
        
        # Mock PostalCode
        mock_postal = MagicMock(spec=PostalCode)
        mock_postal.value = "10115"

        stations = repo.find_stations_by_postal_code(mock_postal)

        self.assertEqual(len(stations), 2)
        self.assertIsInstance(stations[0], ChargingStation)
        
        # Verify attributes of the first station
        # Note: The order depends on DataFrame order, which is preserved here
        self.assertEqual(stations[0].latitude, 52.5323)
        self.assertEqual(stations[0].longitude, 13.3846)
        self.assertEqual(stations[0].power_kw, 22.0)
        self.assertEqual(stations[0].postal_code, mock_postal)

    @patch("pandas.read_csv")
    def test_find_stations_by_postal_code_not_found(self, mock_read_csv):
        """
        Test finding stations returns empty list when none exist for postal code.
        """
        mock_df = pd.DataFrame(self.raw_data)
        mock_read_csv.return_value = mock_df

        repo = CSVChargingStationRepository(self.mock_file_path)
        
        mock_postal = MagicMock(spec=PostalCode)
        mock_postal.value = "99999"  # Postal code not in data

        stations = repo.find_stations_by_postal_code(mock_postal)

        self.assertEqual(stations, [])

if __name__ == '__main__':
    unittest.main()