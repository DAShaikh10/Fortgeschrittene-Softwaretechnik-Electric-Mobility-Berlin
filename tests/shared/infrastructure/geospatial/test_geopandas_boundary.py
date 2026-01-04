"""Tests for the GeopandasBoundary infrastructure implementation."""

# pylint: disable=redefined-outer-name

import json
import geopandas as gpd
import pytest
from shapely.geometry import Polygon

from src.shared.infrastructure.geospatial import GeopandasBoundary


@pytest.fixture
def polygon_gdf_data():
    """Create a GeoDataFrame containing a single polygon for testing."""
    polygon = Polygon([(13.4, 52.5), (13.5, 52.5), (13.5, 52.6), (13.4, 52.6), (13.4, 52.5)])
    return gpd.GeoDataFrame(geometry=[polygon])


def test_from_wkt_creates_non_empty_boundary():
    """Test that the GeopandasBoundary can be created from a WKT string."""
    boundary = GeopandasBoundary.from_wkt("POLYGON ((13.4 52.5, 13.5 52.5, 13.5 52.6, 13.4 52.6, 13.4 52.5))")

    assert isinstance(boundary.gdf, gpd.GeoDataFrame)
    assert isinstance(boundary.geometry, gpd.GeoSeries)
    assert not boundary.is_empty()


def test_constructor_accepts_geodataframe(polygon_gdf_data):
    """Test that the GeopandasBoundary can be constructed with a GeoDataFrame."""
    boundary = GeopandasBoundary(polygon_gdf_data)

    assert boundary.gdf is polygon_gdf_data
    assert not boundary.is_empty()


def test_from_wkt_rejects_empty_string():
    """Test that from_wkt raises ValueError when given an empty string."""
    with pytest.raises(ValueError):
        GeopandasBoundary.from_wkt("")


def test_from_wkt_rejects_none():
    """Test that from_wkt raises ValueError when given None."""
    with pytest.raises(ValueError):
        GeopandasBoundary.from_wkt(None)


def test_constructor_rejects_non_geodataframe():
    """Test that the GeopandasBoundary constructor raises TypeError for invalid input."""
    with pytest.raises(TypeError):
        GeopandasBoundary("not a geodataframe")


def test_constructor_rejects_none():
    """Test that the GeopandasBoundary constructor raises ValueError for None."""
    with pytest.raises(ValueError, match="Boundary geometry cannot be None"):
        GeopandasBoundary(None)


def test_geopandas_boundary_delegates_to_geodataframe_methods():
    """Test that GeopandasBoundary delegates methods to the underlying GeoDataFrame."""
    boundary = GeopandasBoundary.from_wkt("POLYGON ((13.4 52.5, 13.5 52.5, 13.5 52.6, 13.4 52.6, 13.4 52.5))")

    # __getattr__ should proxy attributes like shape
    assert boundary.shape[0] == 1

    # to_json should delegate to underlying GeoDataFrame
    geojson = json.loads(boundary.to_json())
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson.get("features", [])) == 1
