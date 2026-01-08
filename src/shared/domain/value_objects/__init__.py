"""
src.shared.domain.value_objects - Shared Kernel Value Objects module.
"""

from .postal_code import PostalCode
from .boundary import Boundary
from .geo_location import GeoLocation
from .population_data import PopulationData
from .power_capacity import PowerCapacity

__all__ = [
    "PostalCode",
    "Boundary",
    "GeoLocation",
    "PopulationData",
    "PowerCapacity",
]
