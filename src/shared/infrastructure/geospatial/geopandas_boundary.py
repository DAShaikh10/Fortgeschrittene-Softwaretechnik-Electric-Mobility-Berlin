"""
Geopandas-backed implementation of the domain Boundary abstraction.
"""

from dataclasses import dataclass
from typing import Optional

import geopandas as gpd

from src.shared.domain.value_objects import Boundary


@dataclass(frozen=True)
class GeopandasBoundary(Boundary):
    """Concrete boundary backed by a GeoDataFrame."""

    gdf: gpd.GeoDataFrame

    def __post_init__(self):
        if self.gdf is None:
            raise ValueError("Boundary geometry cannot be None.")
        if not isinstance(self.gdf, gpd.GeoDataFrame):
            raise TypeError("geometry must be a GeoDataFrame.")

    def is_empty(self) -> bool:  # type: ignore[override]
        return self.gdf.empty

    @classmethod
    def from_wkt(cls, boundary_wkt: Optional[str]) -> "GeopandasBoundary":
        """Create a boundary from a WKT string."""
        if boundary_wkt is None:
            raise ValueError("Boundary WKT cannot be None.")

        text = str(boundary_wkt).strip()
        if not text:
            raise ValueError("Boundary WKT cannot be empty.")

        gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries.from_wkt([text]))
        return cls(gdf=gdf)

    def to_json(self, *args, **kwargs):  # pragma: no cover - thin delegation
        """Delegate to underlying GeoDataFrame JSON export."""
        return self.gdf.to_json(*args, **kwargs)

    def __getattr__(self, name):  # pragma: no cover - thin delegation
        # Delegate missing attributes to the underlying GeoDataFrame so existing
        # code that expects a GeoDataFrame (e.g., .shape, .columns, .head) continues to work.

        return getattr(self.gdf, name)

    @property
    def geometry(self):  # pragma: no cover - thin delegation
        """Return the underlying GeoSeries geometry column for compatibility."""
        return self.gdf.geometry
