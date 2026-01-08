"""
Unit Tests for DemandAnalysisAggregate.

Test categories:
- Factory method tests
- Query tests
- Command tests (update methods)
- Business rule tests
- Event handling tests
- Edge cases and validation
"""

# pylint: disable=redefined-outer-name

import pytest

from src.shared.domain.enums import CoverageAssessment
from src.shared.domain.value_objects import PostalCode
from src.demand.domain.enums import PriorityLevel
from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.domain.value_objects import DemandPriority, Population, StationCount
from src.demand.domain.events import (
    DemandAnalysisCalculatedEvent,
    HighDemandAreaIdentifiedEvent,
)
from src.demand.application.dtos import DemandAnalysisDTO


# Test fixtures
@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def high_priority_data():
    """Data for high priority area (>5000 residents/station)."""
    return {
        "postal_code": PostalCode("10115"),
        "population": 30000,
        "station_count": 5,
    }


@pytest.fixture
def medium_priority_data():
    """Data for medium priority area (2000-5000 residents/station)."""
    return {
        "postal_code": PostalCode("12345"),
        "population": 15000,
        "station_count": 5,
    }


@pytest.fixture
def low_priority_data():
    """Data for low priority area (<2000 residents/station)."""
    return {
        "postal_code": PostalCode("13579"),
        "population": 10000,
        "station_count": 10,
    }


@pytest.fixture
def high_priority_aggregate(high_priority_data):
    """Create a high priority demand analysis aggregate."""
    return DemandAnalysisAggregate.create(**high_priority_data)


@pytest.fixture
def medium_priority_aggregate(medium_priority_data):
    """Create a medium priority demand analysis aggregate."""
    return DemandAnalysisAggregate.create(**medium_priority_data)


@pytest.fixture
def low_priority_aggregate(low_priority_data):
    """Create a low priority demand analysis aggregate."""
    return DemandAnalysisAggregate.create(**low_priority_data)


class TestDemandAnalysisAggregateFactoryMethods:
    """Test factory methods for creating aggregates."""

    def test_create_returns_aggregate_with_calculated_priority(self, valid_postal_code):
        """Test create factory method calculates priority automatically."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=30000, station_count=5)

        assert isinstance(aggregate, DemandAnalysisAggregate)
        assert aggregate.postal_code == valid_postal_code
        assert aggregate.get_population() == 30000
        assert aggregate.get_station_count() == 5
        assert aggregate.demand_priority is not None
        assert isinstance(aggregate.demand_priority, DemandPriority)

    def test_create_calculates_high_priority_correctly(self, valid_postal_code):
        """Test that create calculates high priority for >5000 residents/station."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=30000, station_count=5)

        assert aggregate.demand_priority.level == PriorityLevel.HIGH
        assert aggregate.demand_priority.residents_per_station == 6000.0

    def test_create_calculates_medium_priority_correctly(self, valid_postal_code):
        """Test that create calculates medium priority for 2000-5000 residents/station."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=15000, station_count=5)

        assert aggregate.demand_priority.level == PriorityLevel.MEDIUM
        assert aggregate.demand_priority.residents_per_station == 3000.0

    def test_create_calculates_low_priority_correctly(self, valid_postal_code):
        """Test that create calculates low priority for <2000 residents/station."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=10000, station_count=10)

        assert aggregate.demand_priority.level == PriorityLevel.LOW
        assert aggregate.demand_priority.residents_per_station == 1000.0

    def test_create_with_zero_stations_sets_high_priority(self, valid_postal_code):
        """Test that create with zero stations results in high priority."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=50000, station_count=0)

        assert aggregate.demand_priority.level == PriorityLevel.HIGH
        assert aggregate.demand_priority.residents_per_station == 50000.0

    def test_create_from_existing_uses_provided_priority(self, valid_postal_code):
        """Test create_from_existing uses the provided priority without recalculation."""
        existing_priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3500.0)

        aggregate = DemandAnalysisAggregate.create_from_existing(
            postal_code=valid_postal_code,
            population=20000,
            station_count=10,
            existing_priority=existing_priority,
        )

        assert aggregate.demand_priority == existing_priority
        # Priority is not recalculated, so it matches the provided one
        assert aggregate.demand_priority.residents_per_station == 3500.0

    def test_create_from_existing_is_used_for_reconstitution(self, valid_postal_code):
        """Test that create_from_existing is suitable for repository reconstitution."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=7000.0)

        aggregate = DemandAnalysisAggregate.create_from_existing(
            postal_code=valid_postal_code,
            population=35000,
            station_count=5,
            existing_priority=priority,
        )

        assert isinstance(aggregate, DemandAnalysisAggregate)
        assert aggregate.postal_code == valid_postal_code


class TestDemandAnalysisAggregateInvariantValidation:
    """Test invariant validation in __post_init__."""

    def test_create_raises_error_for_negative_population(self, valid_postal_code):
        """Test that negative population raises ValueError."""
        with pytest.raises(ValueError, match="Population cannot be negative"):
            DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=-1000, station_count=5)

    def test_create_raises_error_for_negative_station_count(self, valid_postal_code):
        """Test that negative station count raises ValueError."""
        with pytest.raises(ValueError, match="Station count cannot be negative"):
            DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=20000, station_count=-5)

    def test_create_raises_error_for_none_priority(self, valid_postal_code):
        """Test that None priority raises ValueError (requires factory method)."""
        with pytest.raises(ValueError, match="Demand priority must be provided"):
            DemandAnalysisAggregate(
                postal_code=valid_postal_code,
                population=Population(20000),
                station_count=StationCount(5),
                demand_priority=None,
            )

    def test_create_accepts_zero_population(self, valid_postal_code):
        """Test that zero population is valid."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=0, station_count=5)

        assert aggregate.get_population() == 0

    def test_create_accepts_zero_stations(self, valid_postal_code):
        """Test that zero stations is valid."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=20000, station_count=0)

        assert aggregate.get_station_count() == 0


class TestDemandAnalysisAggregateQueries:
    """Test query methods."""

    def test_get_postal_code_returns_postal_code(self, high_priority_aggregate):
        """Test get_postal_code returns the postal code value object."""
        assert high_priority_aggregate.get_postal_code().value == "10115"
        assert isinstance(high_priority_aggregate.get_postal_code(), PostalCode)

    def test_get_population_returns_population(self, high_priority_aggregate):
        """Test get_population returns the population count."""
        assert high_priority_aggregate.get_population() == 30000

    def test_get_station_count_returns_station_count(self, high_priority_aggregate):
        """Test get_station_count returns the station count."""
        assert high_priority_aggregate.get_station_count() == 5

    def test_get_demand_priority_returns_priority_object(self, high_priority_aggregate):
        """Test get_demand_priority returns the DemandPriority value object."""
        priority = high_priority_aggregate.get_demand_priority()

        assert isinstance(priority, DemandPriority)
        assert priority.level == PriorityLevel.HIGH

    def test_get_residents_per_station_calculates_ratio(self, high_priority_aggregate):
        """Test get_residents_per_station calculates correct ratio."""
        assert high_priority_aggregate.get_residents_per_station() == 6000.0

    def test_get_residents_per_station_with_zero_stations(self, valid_postal_code):
        """Test get_residents_per_station returns population when no stations."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=50000, station_count=0)

        assert aggregate.get_residents_per_station() == 50000.0

    def test_get_residents_per_station_with_fractional_result(self, valid_postal_code):
        """Test get_residents_per_station handles fractional results."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=10000, station_count=3)

        assert aggregate.get_residents_per_station() == pytest.approx(3333.33, rel=0.01)


class TestDemandAnalysisAggregateBusinessRules:
    """Test business rule methods."""

    def test_is_high_priority_returns_true_for_high_priority(self, high_priority_aggregate):
        """Test is_high_priority returns True for high priority areas."""
        assert high_priority_aggregate.is_high_priority() is True

    def test_is_high_priority_returns_false_for_medium_priority(self, medium_priority_aggregate):
        """Test is_high_priority returns False for medium priority areas."""
        assert medium_priority_aggregate.is_high_priority() is False

    def test_is_high_priority_returns_false_for_low_priority(self, low_priority_aggregate):
        """Test is_high_priority returns False for low priority areas."""
        assert low_priority_aggregate.is_high_priority() is False

    def test_needs_infrastructure_expansion_true_above_3000(self, high_priority_aggregate):
        """Test needs_infrastructure_expansion returns True when ratio > 3000."""
        assert high_priority_aggregate.needs_infrastructure_expansion() is True

    def test_needs_infrastructure_expansion_false_below_3000(self, low_priority_aggregate):
        """Test needs_infrastructure_expansion returns False when ratio < 3000."""
        assert low_priority_aggregate.needs_infrastructure_expansion() is False

    def test_needs_infrastructure_expansion_at_boundary(self, valid_postal_code):
        """Test needs_infrastructure_expansion at 3000 threshold."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=15000, station_count=5)

        # 3000 residents/station - exactly at boundary (not >3000)
        assert aggregate.needs_infrastructure_expansion() is False

    def test_get_coverage_assessment_returns_critical(self, valid_postal_code):
        """Test get_coverage_assessment returns CRITICAL for >10000 ratio."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=50000, station_count=4)

        assert aggregate.get_coverage_assessment() == CoverageAssessment.CRITICAL

    def test_get_coverage_assessment_returns_poor(self, valid_postal_code):
        """Test get_coverage_assessment returns POOR for 5000-10000 ratio."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=30000, station_count=5)

        assert aggregate.get_coverage_assessment() == CoverageAssessment.POOR

    def test_get_coverage_assessment_returns_adequate(self, valid_postal_code):
        """Test get_coverage_assessment returns ADEQUATE for 2000-5000 ratio."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=15000, station_count=5)

        assert aggregate.get_coverage_assessment() == CoverageAssessment.ADEQUATE

    def test_get_coverage_assessment_returns_good(self, valid_postal_code):
        """Test get_coverage_assessment returns GOOD for <2000 ratio."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=10000, station_count=10)

        assert aggregate.get_coverage_assessment() == CoverageAssessment.GOOD

    def test_calculate_recommended_stations_with_default_target(self, high_priority_aggregate):
        """Test calculate_recommended_stations with default target ratio (2000)."""
        # 30000 / 2000 = 15 total needed, 5 existing = 10 additional
        additional = high_priority_aggregate.calculate_recommended_stations()

        assert additional == 10

    def test_calculate_recommended_stations_with_custom_target(self, high_priority_aggregate):
        """Test calculate_recommended_stations with custom target ratio."""
        # 30000 / 1000 = 30 total needed, 5 existing = 25 additional
        additional = high_priority_aggregate.calculate_recommended_stations(target_ratio=1000.0)

        assert additional == 25

    def test_calculate_recommended_stations_when_already_meeting_target(self, low_priority_aggregate):
        """Test calculate_recommended_stations returns 0 when target already met."""
        # 10000 / 2000 = 5 total needed, 10 existing = 0 additional (already exceeded)
        additional = low_priority_aggregate.calculate_recommended_stations(target_ratio=2000.0)

        assert additional == 0

    def test_calculate_recommended_stations_raises_error_for_zero_target(self, high_priority_aggregate):
        """Test calculate_recommended_stations raises error for zero or negative target."""
        with pytest.raises(ValueError, match="Target ratio must be positive"):
            high_priority_aggregate.calculate_recommended_stations(target_ratio=0.0)

    def test_calculate_recommended_stations_raises_error_for_negative_target(self, high_priority_aggregate):
        """Test calculate_recommended_stations raises error for negative target."""
        with pytest.raises(ValueError, match="Target ratio must be positive"):
            high_priority_aggregate.calculate_recommended_stations(target_ratio=-1000.0)


class TestDemandAnalysisAggregateCommands:
    """Test command methods that modify state."""

    def test_update_population_changes_population(self, high_priority_aggregate):
        """Test update_population changes the population value."""
        high_priority_aggregate.update_population(40000)

        assert high_priority_aggregate.get_population() == 40000

    def test_update_population_recalculates_priority(self, high_priority_aggregate):
        """Test update_population recalculates demand priority."""
        original_priority = high_priority_aggregate.demand_priority

        # Update to lower population - should change priority
        high_priority_aggregate.update_population(8000)

        # 8000 / 5 = 1600 residents/station -> LOW priority
        assert high_priority_aggregate.demand_priority.level == PriorityLevel.LOW
        assert high_priority_aggregate.demand_priority != original_priority

    def test_update_population_raises_error_for_negative_value(self, high_priority_aggregate):
        """Test update_population raises error for negative population."""
        with pytest.raises(ValueError, match="Population cannot be negative"):
            high_priority_aggregate.update_population(-5000)

    def test_update_station_count_changes_station_count(self, high_priority_aggregate):
        """Test update_station_count changes the station count value."""
        high_priority_aggregate.update_station_count(10)

        assert high_priority_aggregate.get_station_count() == 10

    def test_update_station_count_recalculates_priority(self, high_priority_aggregate):
        """Test update_station_count recalculates demand priority."""
        # 30000 / 5 = 6000 -> HIGH
        assert high_priority_aggregate.demand_priority.level == PriorityLevel.HIGH

        # Update to more stations
        high_priority_aggregate.update_station_count(20)

        # 30000 / 20 = 1500 residents/station -> LOW priority
        assert high_priority_aggregate.demand_priority.level == PriorityLevel.LOW

    def test_update_station_count_raises_error_for_negative_value(self, high_priority_aggregate):
        """Test update_station_count raises error for negative station count."""
        with pytest.raises(ValueError, match="Station count cannot be negative"):
            high_priority_aggregate.update_station_count(-3)

    def test_calculate_demand_priority_recalculates_and_returns(self, high_priority_aggregate):
        """Test calculate_demand_priority recalculates and returns priority."""
        priority = high_priority_aggregate.calculate_demand_priority()

        assert isinstance(priority, DemandPriority)
        assert priority == high_priority_aggregate.demand_priority

    def test_update_population_to_zero_is_valid(self, high_priority_aggregate):
        """Test that updating population to zero is valid."""
        high_priority_aggregate.update_population(0)

        assert high_priority_aggregate.get_population() == 0

    def test_update_station_count_to_zero_is_valid(self, high_priority_aggregate):
        """Test that updating station count to zero is valid."""
        high_priority_aggregate.update_station_count(0)

        assert high_priority_aggregate.get_station_count() == 0
        assert high_priority_aggregate.demand_priority.level == PriorityLevel.HIGH


class TestDemandAnalysisAggregateEventHandling:
    """Test domain event handling."""

    def test_calculate_demand_priority_emits_demand_calculated_event(self, high_priority_aggregate):
        """Test that calculate_demand_priority emits DemandAnalysisCalculatedEvent."""
        high_priority_aggregate.calculate_demand_priority()

        events = high_priority_aggregate.get_domain_events()

        # Should have at least the DemandAnalysisCalculatedEvent
        assert any(isinstance(e, DemandAnalysisCalculatedEvent) for e in events)

    def test_calculate_demand_priority_emits_high_demand_event_for_high_priority(self, high_priority_aggregate):
        """Test that high priority areas emit HighDemandAreaIdentifiedEvent."""
        high_priority_aggregate.calculate_demand_priority()

        events = high_priority_aggregate.get_domain_events()

        # Should have both DemandAnalysisCalculated and HighDemandAreaIdentified
        assert any(isinstance(e, DemandAnalysisCalculatedEvent) for e in events)
        assert any(isinstance(e, HighDemandAreaIdentifiedEvent) for e in events)

    def test_calculate_demand_priority_no_high_demand_event_for_low_priority(self, low_priority_aggregate):
        """Test that low priority areas don't emit HighDemandAreaIdentifiedEvent."""
        low_priority_aggregate.calculate_demand_priority()

        events = low_priority_aggregate.get_domain_events()

        # Should have DemandAnalysisCalculated but NOT HighDemandAreaIdentified
        assert any(isinstance(e, DemandAnalysisCalculatedEvent) for e in events)
        assert not any(isinstance(e, HighDemandAreaIdentifiedEvent) for e in events)

    def test_demand_calculated_event_contains_correct_data(self, valid_postal_code):
        """Test that DemandAnalysisCalculatedEvent contains correct data."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=25000, station_count=4)

        aggregate.calculate_demand_priority()
        events = aggregate.get_domain_events()

        demand_event = next((e for e in events if isinstance(e, DemandAnalysisCalculatedEvent)), None)

        assert demand_event is not None
        assert demand_event.postal_code == valid_postal_code
        assert demand_event.population == 25000
        assert demand_event.station_count == 4
        assert demand_event.demand_priority.level == PriorityLevel.HIGH

    def test_high_demand_event_contains_urgency_score(self, high_priority_aggregate):
        """Test that HighDemandAreaIdentifiedEvent contains urgency score."""
        high_priority_aggregate.calculate_demand_priority()

        events = high_priority_aggregate.get_domain_events()
        high_demand_event = next((e for e in events if isinstance(e, HighDemandAreaIdentifiedEvent)), None)

        assert high_demand_event is not None
        assert high_demand_event.urgency_score > 0
        assert isinstance(high_demand_event.urgency_score, float)

    def test_update_population_emits_events(self, high_priority_aggregate):
        """Test that update_population triggers event emission."""
        high_priority_aggregate.clear_domain_events()
        high_priority_aggregate.update_population(35000)

        events = high_priority_aggregate.get_domain_events()
        assert len(events) > 0

    def test_update_station_count_emits_events(self, high_priority_aggregate):
        """Test that update_station_count triggers event emission."""
        high_priority_aggregate.clear_domain_events()
        high_priority_aggregate.update_station_count(8)

        events = high_priority_aggregate.get_domain_events()
        assert len(events) > 0


class TestDemandAnalysisAggregateDataConversion:
    """Test data conversion methods."""

    @staticmethod
    def _to_dict(aggregate: DemandAnalysisAggregate) -> dict:
        """Convert aggregate to DTO dict without exposing domain internals."""
        return DemandAnalysisDTO.from_aggregate(aggregate).to_dict()

    def test_to_dict_returns_correct_structure(self, high_priority_aggregate):
        """Test to_dict returns dictionary with all business metrics."""
        result = self._to_dict(high_priority_aggregate)

        assert isinstance(result, dict)
        assert "postal_code" in result
        assert "population" in result
        assert "station_count" in result
        assert "demand_priority" in result
        assert "residents_per_station" in result
        assert "urgency_score" in result
        assert "is_high_priority" in result
        assert "needs_expansion" in result
        assert "coverage_assessment" in result

    def test_to_dict_contains_correct_values(self, high_priority_aggregate):
        """Test that to_dict contains correct values."""
        result = self._to_dict(high_priority_aggregate)

        assert result["postal_code"] == "10115"
        assert result["population"] == 30000
        assert result["station_count"] == 5
        assert result["demand_priority"] == "High"
        assert result["residents_per_station"] == 6000.0
        assert result["is_high_priority"] is True
        assert result["needs_expansion"] is True
        assert result["coverage_assessment"] == "POOR"

    def test_to_dict_handles_low_priority_area(self, low_priority_aggregate):
        """Test to_dict works correctly for low priority area."""
        result = self._to_dict(low_priority_aggregate)

        assert result["demand_priority"] == "Low"
        assert result["is_high_priority"] is False
        assert result["needs_expansion"] is False
        assert result["coverage_assessment"] == "GOOD"

    def test_to_dict_urgency_score_is_float(self, high_priority_aggregate):
        """Test that urgency_score in to_dict is a float."""
        result = self._to_dict(high_priority_aggregate)

        assert isinstance(result["urgency_score"], float)
        assert result["urgency_score"] > 0


class TestDemandAnalysisAggregateEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_aggregate_with_very_large_population(self, valid_postal_code):
        """Test aggregate handles very large population."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=1000000, station_count=50)

        assert aggregate.get_population() == 1000000
        assert aggregate.get_residents_per_station() == 20000.0

    def test_aggregate_with_very_large_station_count(self, valid_postal_code):
        """Test aggregate handles very large station count."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=50000, station_count=1000)

        assert aggregate.get_station_count() == 1000
        assert aggregate.demand_priority.level == PriorityLevel.LOW

    def test_aggregate_with_equal_population_and_stations(self, valid_postal_code):
        """Test aggregate with 1:1 ratio."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=1000, station_count=1000)

        assert aggregate.get_residents_per_station() == 1.0
        assert aggregate.demand_priority.level == PriorityLevel.LOW

    def test_aggregate_priority_boundary_at_5000(self, valid_postal_code):
        """Test priority boundary at exactly 5000 residents/station."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=25000, station_count=5)

        # Exactly 5000 - should still be MEDIUM (>5000 is HIGH)
        assert aggregate.get_residents_per_station() == 5000.0
        assert aggregate.demand_priority.level == PriorityLevel.MEDIUM

    def test_aggregate_priority_boundary_at_2000(self, valid_postal_code):
        """Test priority boundary at exactly 2000 residents/station."""
        aggregate = DemandAnalysisAggregate.create(postal_code=valid_postal_code, population=10000, station_count=5)

        # Exactly 2000 - should still be LOW (>2000 is MEDIUM)
        assert aggregate.get_residents_per_station() == 2000.0
        assert aggregate.demand_priority.level == PriorityLevel.LOW

    def test_different_valid_postal_codes(self):
        """Test aggregate works with all valid Berlin postal code ranges."""
        postal_codes = ["10115", "12345", "13579", "14195"]

        for code in postal_codes:
            aggregate = DemandAnalysisAggregate.create(postal_code=PostalCode(code), population=20000, station_count=5)
            assert aggregate.postal_code.value == code

    def test_aggregate_state_consistency_after_multiple_updates(self, high_priority_aggregate):
        """Test that aggregate maintains consistency after multiple updates."""
        # Multiple updates
        high_priority_aggregate.update_population(25000)
        high_priority_aggregate.update_station_count(8)
        high_priority_aggregate.update_population(32000)

        # State should be consistent
        assert high_priority_aggregate.get_population() == 32000
        assert high_priority_aggregate.get_station_count() == 8
        assert high_priority_aggregate.get_residents_per_station() == 4000.0
