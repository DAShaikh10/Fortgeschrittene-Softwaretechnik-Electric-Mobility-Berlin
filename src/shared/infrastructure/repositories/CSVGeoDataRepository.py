"""
CSV-based implementation of GeoDataRepository.
"""

from src.discovery.domain.entities import PostalCode
from src.shared.domain.value_objects import GeoLocation

from .CSVRepository import CSVRepository
from .GeoDataRepository import GeoDataRepository


class CSVGeoDataRepository(GeoDataRepository, CSVRepository):
    """
    CSV-based implementation of `GeoDataRepository`.

    This repository provides geographic boundary data for postal codes.
    """

    def __init__(self, file_path: str):
        """
        Initialize `CSVGeoDataRepository` with CSV file path.

        Args:
            file_path (str): Path to the geolocation data CSV file.
        """
        super().__init__(file_path)

        self._df = self._load_csv(sep=";")
        self._transform()

    # Abstract method implementation.
    def _transform(self):
        """
        Transform the loaded DataFrame for consistent data types.
        """

    def fetch_geolocation_data(self, postal_code: PostalCode):
        """
        Fetch geographic data for a given postal code.

        Args:
            postal_code (PostalCode): The postal code to fetch geographic data for.

        Returns:
            GeoLocation: Geographic location data for the given postal code or None if not found.
        """

        result = self._df[self._df["PLZ"] == postal_code.value]
        if result.empty:
            return None

        boundary = result.iloc[0]["geometry"]
        return GeoLocation(postal_code=postal_code, boundary=boundary)
