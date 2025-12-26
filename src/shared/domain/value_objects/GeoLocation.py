"""
GeoLocation Value Object Module.
"""

import logging
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass, field

import geopandas as gpd

from src.shared.domain.exceptions import InvalidGeoLocationError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.shared.domain.value_objects.PostalCode import PostalCode


def _process_boundary(boundary_wkt: str) -> gpd.GeoDataFrame:
    """
    Process WKT boundary string into a GeoDataFrame.

    Args:
        boundary_wkt: WKT string representation of the boundary geometry

    Returns:
        GeoDataFrame with the boundary geometry
    """
    wkt_length = len(boundary_wkt) if boundary_wkt else 0
    logger.info("_process_boundary called with WKT length: %d", wkt_length)
    if not boundary_wkt:
        logger.warning("Empty boundary_wkt provided")
        return None
    try:
        gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries.from_wkt([boundary_wkt]))
        logger.info("✓ Successfully created GeoDataFrame with shape: %s", gdf.shape)
        return gdf
    except Exception as e:
        logger.error("Error processing boundary WKT: %s", e, exc_info=True)
        raise


@dataclass(frozen=True)
class GeoLocation:
    """
    Entity: Represents geographic location data.

    This entity encapsulates geographic information such as coordinates and boundaries.
    """

    postal_code: "PostalCode"
    boundary: Any = field(default=None, repr=False)

    def __post_init__(self):
        """
        Process and validate the boundary data on creation.
        """
        logger.info("GeoLocation __post_init__ called for postal_code: %s", self.postal_code)
        logger.info("Initial boundary type: %s", type(self.boundary))
        boundary_preview = str(self.boundary)[:200] if self.boundary else "None"
        logger.info("Initial boundary value (first 200 chars): %s", boundary_preview)

        # Process the boundary if it's a WKT string
        if isinstance(self.boundary, str):
            logger.info("Boundary is a string, processing WKT...")
            processed_boundary = _process_boundary(self.boundary)
            logger.info("Processed boundary type: %s", type(processed_boundary))
            if processed_boundary is not None:
                logger.info("Processed boundary shape: %s", processed_boundary.shape)
                logger.info("Processed boundary columns: %s", processed_boundary.columns.tolist())
            # Use object.__setattr__ because the dataclass is frozen
            object.__setattr__(self, "boundary", processed_boundary)
        # Validate
        if self.boundary is None or (isinstance(self.boundary, gpd.GeoDataFrame) and self.boundary.empty):
            logger.error("GeoLocation validation failed - boundary is None or empty")
            raise InvalidGeoLocationError("Geo Location boundary cannot be None or empty.")

        logger.info("✓ GeoLocation created successfully for %s", self.postal_code)

    @property
    def empty(self) -> bool:
        """
        Check if the GeoLocation has an empty boundary.

        Returns:
            True if boundary is None or empty, False otherwise
        """
        return self.boundary is None or (isinstance(self.boundary, gpd.GeoDataFrame) and self.boundary.empty)
