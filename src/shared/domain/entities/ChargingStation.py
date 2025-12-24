"""
Shared Domain Entity - Charging Station Module.
"""


class ChargingStation:
    """
    Entity within the PostalCodeArea aggregate.
    Represents a single charging station.
    """

    def __init__(self, postal_code: str, latitude: float, longitude: float, power_kw: float):
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.power_kw = power_kw
