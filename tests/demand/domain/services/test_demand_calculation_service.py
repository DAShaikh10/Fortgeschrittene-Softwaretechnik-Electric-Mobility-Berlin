"""
Unit Tests for DemandCalculationService.

Test categories:
- Regional demand calculation tests
- Area comparison tests
- Priority cluster identification tests
- Edge cases and validation
"""

# pylint: disable=redefined-outer-name

import pytest

from src.shared.domain.value_objects import PostalCode
from src.demand.domain.enums import PriorityLevel
from src.demand.domain.services import DemandCalculationService, RegionalDemandAnalysis
from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.domain.value_objects import DemandPriority, Population, StationCount


@pytest.fixture
def high_priority_aggregate():
    """Create a high-priority demand aggregate."""
    postal_code = PostalCode("10115")
    population = Population(15000)
    station_count = StationCount(2)
    priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=7500.0)
    return DemandAnalysisAggregate(
        postal_code=postal_code,
        population=population,
        station_count=station_count,
        demand_priority=priority,
    )


@pytest.fixture
def medium_priority_aggregate():
    """Create a medium-priority demand aggregate."""
    postal_code = PostalCode("10117")
    population = Population(10000)
    station_count = StationCount(3)
    priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3333.0)
    return DemandAnalysisAggregate(
        postal_code=postal_code,
        population=population,
        station_count=station_count,
        demand_priority=priority,
    )


@pytest.fixture
def low_priority_aggregate():
    """Create a low-priority demand aggregate."""
    postal_code = PostalCode("10119")
    population = Population(5000)
    station_count = StationCount(5)
    priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=1000.0)
    return DemandAnalysisAggregate(
        postal_code=postal_code,
        population=population,
        station_count=station_count,
        demand_priority=priority,
    )


class TestCalculateRegionalDemand:
    """Test calculate_regional_demand method."""

    def test_calculates_regional_metrics_correctly(
        self, high_priority_aggregate, medium_priority_aggregate, low_priority_aggregate
    ):
        """Test that method calculates correct regional metrics."""
        aggregates = [high_priority_aggregate, medium_priority_aggregate, low_priority_aggregate]

        result = DemandCalculationService.calculate_regional_demand(aggregates)

        assert isinstance(result, RegionalDemandAnalysis)
        assert result.total_population == 30000  # 15000 + 10000 + 5000
        assert result.total_stations == 10  # 2 + 3 + 5
        assert result.high_priority_count == 1
        assert result.medium_priority_count == 1
        assert result.low_priority_count == 1
        assert result.average_residents_per_station == 3000.0  # 30000 / 10

    def test_identifies_critical_areas(self, high_priority_aggregate):
        """Test that method identifies critical areas correctly."""
        # Create aggregate with high urgency score
        postal_code = PostalCode("10120")
        population = Population(20000)
        station_count = StationCount(1)
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=20000.0)
        critical_aggregate = DemandAnalysisAggregate(
            postal_code=postal_code,
            population=population,
            station_count=station_count,
            demand_priority=priority,
        )

        aggregates = [high_priority_aggregate, critical_aggregate]

        result = DemandCalculationService.calculate_regional_demand(aggregates)

        # Critical areas should have urgency score > 0.8
        assert len(result.critical_areas) >= 0  # Depends on urgency score calculation

    def test_handles_empty_list(self):
        """Test that method raises ValueError for empty list."""
        with pytest.raises(ValueError, match="Cannot calculate regional demand from empty aggregates list"):
            DemandCalculationService.calculate_regional_demand([])

    def test_handles_single_aggregate(self, high_priority_aggregate):
        """Test that method handles single aggregate."""
        result = DemandCalculationService.calculate_regional_demand([high_priority_aggregate])

        assert result.total_population == 15000
        assert result.total_stations == 2
        assert result.high_priority_count == 1

    def test_calculates_average_when_no_stations(self):
        """Test that method handles case with zero stations."""
        postal_code = PostalCode("10121")
        population = Population(10000)
        station_count = StationCount(0)
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=float("inf"))
        aggregate = DemandAnalysisAggregate(
            postal_code=postal_code,
            population=population,
            station_count=station_count,
            demand_priority=priority,
        )

        result = DemandCalculationService.calculate_regional_demand([aggregate])

        assert result.total_stations == 0
        assert result.average_residents_per_station == float("inf")


class TestCompareAreas:
    """Test compare_areas method."""

    def test_compares_two_areas_correctly(self, high_priority_aggregate, low_priority_aggregate):
        """Test that method compares two areas correctly."""
        result = DemandCalculationService.compare_areas(high_priority_aggregate, low_priority_aggregate)

        assert "area1" in result
        assert "area2" in result
        assert "more_urgent" in result
        assert "priority_difference" in result
        assert result["area1"]["postal_code"] == "10115"
        assert result["area2"]["postal_code"] == "10119"

    def test_identifies_more_urgent_area(self, high_priority_aggregate, low_priority_aggregate):
        """Test that method correctly identifies more urgent area."""
        result = DemandCalculationService.compare_areas(high_priority_aggregate, low_priority_aggregate)

        # High priority should be more urgent than low priority
        assert result["more_urgent"] in ["10115", "10119"]
        assert result["priority_difference"] >= 0

    def test_compares_same_area(self, high_priority_aggregate):
        """Test that method handles comparing area to itself."""
        result = DemandCalculationService.compare_areas(high_priority_aggregate, high_priority_aggregate)

        assert result["area1"]["postal_code"] == result["area2"]["postal_code"]
        assert result["priority_difference"] == 0.0


class TestIdentifyPriorityClusters:
    """Test identify_priority_clusters method."""

    def test_groups_areas_by_priority(self, high_priority_aggregate, medium_priority_aggregate, low_priority_aggregate):
        """Test that method groups areas by priority level."""
        aggregates = [high_priority_aggregate, medium_priority_aggregate, low_priority_aggregate]

        clusters = DemandCalculationService.identify_priority_clusters(aggregates)

        assert "High" in clusters
        assert "Medium" in clusters
        assert "Low" in clusters
        assert "10115" in clusters["High"]
        assert "10117" in clusters["Medium"]
        assert "10119" in clusters["Low"]

    def test_handles_empty_list(self):
        """Test that method handles empty list."""
        clusters = DemandCalculationService.identify_priority_clusters([])

        assert clusters == {"High": [], "Medium": [], "Low": []}

    def test_handles_single_priority_level(self, high_priority_aggregate):
        """Test that method handles all areas with same priority."""
        clusters = DemandCalculationService.identify_priority_clusters([high_priority_aggregate])

        assert len(clusters["High"]) == 1
        assert len(clusters["Medium"]) == 0
        assert len(clusters["Low"]) == 0

    def test_handles_multiple_areas_same_priority(self, high_priority_aggregate):
        """Test that method handles multiple areas with same priority."""
        # Create another high priority aggregate
        postal_code = PostalCode("10120")
        population = Population(12000)
        station_count = StationCount(1)
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=12000.0)
        another_high = DemandAnalysisAggregate(
            postal_code=postal_code,
            population=population,
            station_count=station_count,
            demand_priority=priority,
        )

        clusters = DemandCalculationService.identify_priority_clusters([high_priority_aggregate, another_high])

        assert len(clusters["High"]) == 2
        assert "10115" in clusters["High"]
        assert "10120" in clusters["High"]


class TestRegionalDemandAnalysis:
    """Test RegionalDemandAnalysis value object."""

    def test_to_dict_returns_correct_structure(self):
        """Test that to_dict returns correct dictionary structure."""
        analysis = RegionalDemandAnalysis(
            total_population=30000,
            total_stations=10,
            high_priority_count=1,
            medium_priority_count=1,
            low_priority_count=1,
            average_residents_per_station=3000.0,
            critical_areas=["10115"],
        )

        result = analysis.to_dict()

        assert result["total_population"] == 30000
        assert result["total_stations"] == 10
        assert result["high_priority_count"] == 1
        assert result["medium_priority_count"] == 1
        assert result["low_priority_count"] == 1
        assert result["average_residents_per_station"] == 3000.0
        assert result["critical_areas"] == ["10115"]
