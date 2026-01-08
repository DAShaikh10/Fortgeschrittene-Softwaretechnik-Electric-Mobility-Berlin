"""
Shared Domain GeoLocation Value Object.
"""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from src.shared.domain.exceptions import InvalidGeoLocationError
from src.shared.domain.value_objects.boundary import Boundary

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from src.shared.domain.value_objects.postal_code import PostalCode


@dataclass(frozen=True)
class GeoLocation:
    """
    Value Object: Represents geographic location data.

    This value object encapsulates geographic information such as coordinates and boundaries.
    """

    postal_code: "PostalCode"
    boundary: Optional[Boundary] = field(default=None, repr=False)

    def __post_init__(self):
        """Validate the boundary abstraction on creation."""
        logger.info("GeoLocation __post_init__ called for postal_code: %s", self.postal_code)
        logger.debug("Boundary type received: %s", type(self.boundary))

        if self.boundary is None:
            logger.error("GeoLocation validation failed - boundary is None")
            raise InvalidGeoLocationError("Geo Location boundary cannot be None or empty.")

        if not isinstance(self.boundary, Boundary):
            logger.error("Boundary does not implement Boundary interface: %s", type(self.boundary))
            raise InvalidGeoLocationError("Geo Location boundary must implement Boundary abstraction.")

        if self.boundary.is_empty():
            logger.error("GeoLocation validation failed - boundary is empty")
            raise InvalidGeoLocationError("Geo Location boundary cannot be None or empty.")

        logger.info("GeoLocation created successfully for %s", self.postal_code)

    @property
    def empty(self) -> bool:
        """True when the boundary is empty."""
        return self.boundary.is_empty()
