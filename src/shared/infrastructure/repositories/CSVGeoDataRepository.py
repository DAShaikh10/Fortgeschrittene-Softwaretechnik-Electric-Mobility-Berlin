"""
CSV-based implementation of GeoDataRepository.
"""

import geopandas as gpd

from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.infrastructure.geospatial import GeopandasBoundary
from src.shared.infrastructure.logging_config import get_logger

from .CSVRepository import CSVRepository
from .GeoDataRepository import GeoDataRepository

logger = get_logger(__name__)


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

        raw_boundary = result.iloc[0]["geometry"]
        logger.info("Boundary type: %s", type(raw_boundary))
        logger.info("Boundary value (first 200 chars): %s", str(raw_boundary)[:200])

        boundary = self._coerce_boundary(raw_boundary)

        logger.info("Creating GeoLocation object with postal_code=%s", postal_code.value)
        geo_location = GeoLocation(postal_code=postal_code, boundary=boundary)
        logger.info("✓ GeoLocation created successfully")
        return geo_location

    def _coerce_boundary(self, raw_boundary) -> GeopandasBoundary:
        """Convert raw boundary data into a GeopandasBoundary."""
        if isinstance(raw_boundary, GeopandasBoundary):
            return raw_boundary

        if isinstance(raw_boundary, gpd.GeoDataFrame):
            return GeopandasBoundary(raw_boundary)

        if isinstance(raw_boundary, str):
            return GeopandasBoundary.from_wkt(raw_boundary)

        try:
            gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries([raw_boundary]))
            return GeopandasBoundary(gdf)
        except Exception:  # pragma: no cover - defensive logging
            logger.error(
                "Unable to coerce boundary of type %s into GeopandasBoundary", type(raw_boundary), exc_info=True
            )
            raise

    def coerce_boundary(self, raw_boundary) -> GeopandasBoundary:
        """Public method to coerce boundary for testing purposes."""
        return self._coerce_boundary(raw_boundary)

    def get_dataframe_columns(self) -> list:
        """Public method to inspect DataFrame columns for testing."""
        return list(self._df.columns)

    def get_dataframe_column_dtype(self, column: str) -> str:
        """Public method to inspect DataFrame column data type for testing."""
        return str(self._df[column].dtype)

    def get_dataframe_value(self, row: int, column: str):
        """Public method to inspect DataFrame values for testing."""
        return self._df.iloc[row][column]

    def get_all_postal_codes(self) -> list[int]:
        """
        Retrieve all unique postal codes available in the dataset.

        This serves as the 'Source of Truth' for validation in the UI.

        Returns:
            list[int]: List of valid postal code integers.
        """
        try:
            if "PLZ" in self._df.columns:

                return self._df["PLZ"].astype(int).unique().tolist()

            logger.error("Column 'PLZ' not found in GeoData repository.")
            return []
        except Exception as e:
            logger.error("Error retrieving all postal codes: %s", e)
            return []
