"""
CSV-based implementation of GeoDataRepository.
"""

import logging

from src.discovery.domain.entities import PostalCode
from src.shared.domain.value_objects import GeoLocation

from .CSVRepository import CSVRepository
from .GeoDataRepository import GeoDataRepository

logger = logging.getLogger(__name__)


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
        # Convert PLZ to string for consistent comparison with PostalCode value object
        self._df["PLZ"] = self._df["PLZ"].astype(str)
        logger.info("Transformed PLZ column to string type. DataFrame shape: %s", self._df.shape)

    def fetch_geolocation_data(self, postal_code: PostalCode):
        """
        Fetch geographic data for a given postal code.

        Args:
            postal_code (PostalCode): The postal code to fetch geographic data for.

        Returns:
            GeoLocation: Geographic location data for the given postal code or None if not found.
        """
        logger.info("CSVGeoDataRepository: Fetching geolocation for PLZ: %s", postal_code.value)
        logger.info("DataFrame shape: %s", self._df.shape)
        logger.info("DataFrame columns: %s", self._df.columns.tolist())
        logger.info("Available PLZ values (first 10): %s", self._df["PLZ"].head(10).tolist())

        result = self._df[self._df["PLZ"] == postal_code.value]
        logger.info("Query result shape: %s", result.shape)
        if result.empty:
            logger.warning("No geometry found for PLZ: %s", postal_code.value)
            return None

        boundary = result.iloc[0]["geometry"]
        logger.info("Boundary type: %s", type(boundary))
        logger.info("Boundary value (first 200 chars): %s", str(boundary)[:200])

        logger.info("Creating GeoLocation object with postal_code=%s", postal_code.value)
        geo_location = GeoLocation(postal_code=postal_code, boundary=boundary)
        logger.info("✓ GeoLocation created successfully")
        return geo_location
