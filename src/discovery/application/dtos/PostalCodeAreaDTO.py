"""
Data Transfer Object for Postal Code Area information.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PostalCodeAreaDTO:
    """
    DTO for transferring postal code area data to the presentation layer.

    This prevents the UI from:
    - Calling domain methods directly on aggregates
    - Depending on aggregate structure
    - Breaking aggregate encapsulation

    Attributes:
        postal_code: The postal code value as string
        station_count: Total number of charging stations
        fast_charger_count: Number of fast chargers (>=50kW)
        total_capacity_kw: Sum of power capacity in kilowatts
        average_power_kw: Average power per station
        has_fast_charging: Whether area has fast charging capability
        is_well_equipped: Whether area is well-equipped
        coverage_level: Infrastructure coverage level (NO_COVERAGE, POOR, ADEQUATE, GOOD, EXCELLENT)
    """

    postal_code: str
    station_count: int
    fast_charger_count: int
    total_capacity_kw: float
    average_power_kw: float
    has_fast_charging: bool
    is_well_equipped: bool
    coverage_level: str

    @staticmethod
    def from_aggregate(aggregate) -> "PostalCodeAreaDTO":
        """
        Create DTO from aggregate.

        Args:
            aggregate: PostalCodeAreaAggregate domain object

        Returns:
            PostalCodeAreaDTO: Immutable data transfer object
        """
        return PostalCodeAreaDTO(
            postal_code=aggregate.postal_code.value,
            station_count=aggregate.get_station_count(),
            fast_charger_count=aggregate.get_fast_charger_count(),
            total_capacity_kw=aggregate.get_total_capacity_kw(),
            average_power_kw=aggregate.get_average_power_kw(),
            has_fast_charging=aggregate.has_fast_charging(),
            is_well_equipped=aggregate.is_well_equipped(),
            coverage_level=aggregate.get_coverage_level().value,
        )
