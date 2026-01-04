"""DTOs for demand analysis results to keep domain encapsulated."""

from dataclasses import asdict, dataclass
from typing import Dict

from src.demand.domain.aggregates import DemandAnalysisAggregate


@dataclass(frozen=True)
class DemandAnalysisDTO:
    """DTO carrying demand analysis data to external layers."""

    # pylint: disable=too-many-instance-attributes

    postal_code: str
    population: int
    station_count: int
    demand_priority: str
    residents_per_station: float
    urgency_score: float
    is_high_priority: bool
    needs_expansion: bool
    coverage_assessment: str

    @classmethod
    def from_aggregate(cls, aggregate: DemandAnalysisAggregate) -> "DemandAnalysisDTO":
        """Create a DTO from a domain aggregate without exposing internals."""
        return cls(
            postal_code=aggregate.postal_code.value,
            population=aggregate.population.value,
            station_count=aggregate.station_count.value,
            demand_priority=aggregate.demand_priority.level.value,
            residents_per_station=aggregate.demand_priority.residents_per_station,
            urgency_score=aggregate.demand_priority.get_urgency_score(),
            is_high_priority=aggregate.is_high_priority(),
            needs_expansion=aggregate.needs_infrastructure_expansion(),
            coverage_assessment=aggregate.get_coverage_assessment().value,
        )

    def to_dict(self) -> Dict[str, object]:
        """Convert the DTO to a plain dictionary for UI/serialization."""
        return asdict(self)
