"""
src.shared.domain.exceptions - Shared Kernel Domain Exceptions module.
"""

from .invalid_postal_code_exception import InvalidPostalCodeError
from .invalid_geo_location_exception import InvalidGeoLocationError

__all__ = [
    "InvalidPostalCodeError",
    "InvalidGeoLocationError",
]
