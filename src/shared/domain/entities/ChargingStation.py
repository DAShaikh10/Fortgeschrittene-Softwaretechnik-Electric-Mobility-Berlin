"""
Shared Domain Charging Station Entity.
"""

from src.shared.domain.value_objects import PowerCapacity


class ChargingStation:
    """
    Entity within the PostalCodeArea aggregate.
    Represents a single charging station.
    """

    def __init__(self, postal_code: str, latitude: float, longitude: float, power_kw: float):
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.power_capacity = PowerCapacity(kilowatts=power_kw)

    def is_fast_charger(self) -> bool:
        """
        Business rule: Determine if this is a fast charging station.

        Returns:
            bool: True if station has fast charging capability (>= 50 kW)
        """
        return self.power_capacity.is_fast_charging()

    def get_charging_category(self) -> str:
        """
        Business rule: Categorize charging station by power capacity.

        Categories:
        - ULTRA: >= 150 kW (ultra-fast charging)
        - FAST: >= 50 kW (fast charging)
        - NORMAL: < 50 kW (normal charging)

        Returns:
            str: Charging category
        """
        if self.power_capacity.kilowatts >= 150.0:
            return "ULTRA"

        if self.power_capacity.kilowatts >= 50.0:
            return "FAST"

        return "NORMAL"
