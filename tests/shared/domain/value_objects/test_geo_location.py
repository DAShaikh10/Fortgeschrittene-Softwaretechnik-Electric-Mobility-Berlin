"""Unit tests for the GeoLocation value object without infrastructure coupling."""

# pylint: disable=redefined-outer-name

import pytest

from src.shared.domain.exceptions import InvalidGeoLocationError
from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.domain.value_objects.Boundary import Boundary


class FakeBoundary(Boundary):
    """Simple boundary test double."""

    def __init__(self, empty: bool = False):
        self._empty = empty

    def is_empty(self) -> bool:  # type: ignore[override]
        return self._empty


@pytest.fixture
def valid_postal_code():
    """Fixture that provides a valid PostalCode."""
    return PostalCode("10115")


@pytest.fixture
def non_empty_boundary():
    """Fixture that provides a non-empty boundary."""
    return FakeBoundary(empty=False)


@pytest.fixture
def empty_boundary():
    """Fixture that provides an empty boundary."""
    return FakeBoundary(empty=True)


def test_geolocation_accepts_non_empty_boundary(valid_postal_code, non_empty_boundary):
    """Test that GeoLocation can be created with a valid postal code and non-empty boundary."""
    geo_location = GeoLocation(postal_code=valid_postal_code, boundary=non_empty_boundary)

    assert geo_location.postal_code == valid_postal_code
    assert geo_location.boundary is non_empty_boundary
    assert not geo_location.empty


def test_none_boundary_raises_invalid_geo_location(valid_postal_code):
    """Test that passing None as boundary raises an InvalidGeoLocationError."""
    with pytest.raises(InvalidGeoLocationError, match="cannot be None or empty"):
        GeoLocation(postal_code=valid_postal_code, boundary=None)


def test_empty_boundary_raises_invalid_geo_location(valid_postal_code, empty_boundary):
    """Test that passing an empty boundary raises an InvalidGeoLocationError."""
    with pytest.raises(InvalidGeoLocationError, match="cannot be None or empty"):
        GeoLocation(postal_code=valid_postal_code, boundary=empty_boundary)


def test_boundary_must_implement_interface(valid_postal_code):
    """Test that passing an invalid boundary type raises an error."""

    class NotABoundary:
        """A class that does not implement the Boundary interface."""

    with pytest.raises(InvalidGeoLocationError, match="Boundary abstraction"):
        GeoLocation(postal_code=valid_postal_code, boundary=NotABoundary())


def test_empty_property_delegates_to_boundary(valid_postal_code, non_empty_boundary):
    """Test that the empty property reflects the boundary's emptiness."""
    geo_location = GeoLocation(postal_code=valid_postal_code, boundary=non_empty_boundary)
    assert geo_location.empty is False


def test_geolocation_is_immutable(valid_postal_code, non_empty_boundary):
    """Test that GeoLocation attributes are immutable after creation."""
    geo_location = GeoLocation(postal_code=valid_postal_code, boundary=non_empty_boundary)

    with pytest.raises(AttributeError):
        geo_location.postal_code = PostalCode("10178")

    with pytest.raises(AttributeError):
        geo_location.boundary = non_empty_boundary


def test_repr_contains_postal_code(valid_postal_code, non_empty_boundary):
    """Test that the string representation of GeoLocation includes the postal code."""
    geo_location = GeoLocation(postal_code=valid_postal_code, boundary=non_empty_boundary)

    representation = repr(geo_location)
    assert "GeoLocation" in representation
    assert valid_postal_code.value in representation
