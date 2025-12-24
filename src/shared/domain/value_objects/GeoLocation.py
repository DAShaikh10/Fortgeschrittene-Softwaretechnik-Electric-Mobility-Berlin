"""
GeoLocation Value Object Module.
"""

from dataclasses import dataclass

import geopandas as gpd

from src.shared.domain.exceptions import InvalidGeoLocationError


@dataclass(frozen=True)
class GeoLocation:
    """
    Entity: Represents geographic location data.

    This entity encapsulates geographic information such as coordinates and boundaries.
    """

    boundary: gpd.GeoDataFrame

    def __init__(self, boundary):
        self.boundary = gpd.GeoDataFrame(gpd.GeoSeries.from_wkt(boundary)) if boundary else None

    def __post_init__(self):
        """
        Validate postal code on creation (invariant enforcement).
        """

        if self.boundary is None or (isinstance(self.boundary, str) and not self.boundary.strip()):
            raise InvalidGeoLocationError("Geo Location code cannot be None or empty.")
