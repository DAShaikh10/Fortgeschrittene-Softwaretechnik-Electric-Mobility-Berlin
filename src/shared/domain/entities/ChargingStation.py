"""
Shared Domain Charging Station Entity.
"""

from __future__ import annotations

import uuid
from typing import Optional, Union

from src.shared.domain.value_objects import PostalCode, PowerCapacity


class ChargingStation:
    """Entity representing a single charging station."""

    def __init__(
        self,
        postal_code: Union[str, PostalCode],
        latitude: float,
        longitude: float,
        power_kw: Union[float, PowerCapacity],
        station_id: Optional[str] = None,
    ) -> None:
        # Identity
        self.id = station_id or self._generate_id(postal_code, latitude, longitude, power_kw)

        # Normalize postal code to value object
        self.postal_code: PostalCode = postal_code if isinstance(postal_code, PostalCode) else PostalCode(str(postal_code))

        self.latitude = float(latitude)
        self.longitude = float(longitude)

        # Normalize power to value object
        self.power_capacity: PowerCapacity = power_kw if isinstance(power_kw, PowerCapacity) else PowerCapacity(float(power_kw))

    # Derived/compatibility property
    @property
    def power_kw(self) -> float:
        """Return power in kilowatts (backwards compatibility)."""
        return self.power_capacity.kilowatts

    def is_fast_charger(self) -> bool:
        """Fast charger if power is at least 50 kW."""
        return self.power_capacity.kilowatts >= 50.0

    def get_charging_category(self) -> str:
        """Classify charger by power output."""
        power = self.power_capacity.kilowatts
        if power >= 150.0:
            return "ULTRA"
        if power >= 50.0:
            return "FAST"
        return "NORMAL"

    def _generate_id(
        self,
        postal_code: Union[str, PostalCode],
        latitude: float,
        longitude: float,
        power_kw: Union[float, PowerCapacity],
    ) -> str:
        """Generate a deterministic identity based on core attributes."""
        plz_value = postal_code.value if isinstance(postal_code, PostalCode) else str(postal_code)
        power_value = power_kw.kilowatts if isinstance(power_kw, PowerCapacity) else float(power_kw)
        basis = f"{plz_value}:{latitude}:{longitude}:{power_value}"
        return str(uuid.uuid5(uuid.NAMESPACE_URL, basis))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChargingStation):
            return False
        return self.id == other.id

    def __hash__(self) -> int:  # Entities use identity for hashing
        return hash(self.id)

    def __repr__(self) -> str:
        return (
            f"ChargingStation(id={self.id}, postal_code={self.postal_code.value}, "
            f"lat={self.latitude}, lon={self.longitude}, power_kw={self.power_capacity.kilowatts})"
        )
