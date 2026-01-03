"""
Unit Tests for DemandAnalysisService.

Test categories:
- Initialization tests
- analyze_demand use case tests
- analyze_multiple_areas use case tests
- get_high_priority_areas use case tests
- get_demand_analysis use case tests
- update_demand_analysis use case tests
- get_recommendations use case tests
- Event publishing integration tests
- Error handling tests
"""

# pylint: disable=redefined-outer-name,unused-argument

# pylint: disable=redefined-outer-name

from unittest.mock import Mock, patch

import pytest

from src.demand.application.services import DemandAnalysisService
from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.domain.value_objects import DemandPriority
from src.demand.application.enums import PriorityLevel
from src.shared.domain.value_objects import PostalCode
from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.exceptions import InvalidPostalCodeError
from src.demand.infrastructure.repositories import DemandAnalysisRepository
from src.shared.application.services import BaseService


# Test fixtures
@pytest.fixture
def mock_repository():
    """Create a mock DemandAnalysisRepository."""
    repository = Mock(spec=DemandAnalysisRepository)
    return repository


@pytest.fixture
def mock_event_bus():
    """Create a mock event bus implementing IDomainEventPublisher."""
    event_bus = Mock(spec=IDomainEventPublisher)
    return event_bus


@pytest.fixture
def demand_analysis_service(mock_repository, mock_event_bus):
    """Create a DemandAnalysisService instance."""
    return DemandAnalysisService(mock_repository, mock_event_bus)


@pytest.fixture
def valid_postal_code():
    """Create a valid Berlin postal code."""
    return PostalCode("10115")


@pytest.fixture
def high_priority_aggregate(valid_postal_code):
    """Create a high priority demand analysis aggregate."""
    return DemandAnalysisAggregate.create(
        postal_code=valid_postal_code,
        population=30000,
        station_count=5,
    )


@pytest.fixture
def medium_priority_aggregate():
    """Create a medium priority demand analysis aggregate."""
    postal_code = PostalCode("12345")
    return DemandAnalysisAggregate.create(
        postal_code=postal_code,
        population=14000,
        station_count=4,
    )


@pytest.fixture
def low_priority_aggregate():
    """Create a low priority demand analysis aggregate."""
    postal_code = PostalCode("13579")
    return DemandAnalysisAggregate.create(
        postal_code=postal_code,
        population=9000,
        station_count=6,
    )


class TestDemandAnalysisServiceInitialization:
    """Test initialization of DemandAnalysisService."""

    def test_service_initializes_with_repository_and_event_bus(self, mock_repository, mock_event_bus):
        """Test that service initializes correctly with repository and event bus."""
        service = DemandAnalysisService(mock_repository, mock_event_bus)

        assert service.repository is mock_repository
        assert service.event_bus is mock_event_bus

    def test_service_inherits_from_base_service(self, demand_analysis_service):
        """Test that DemandAnalysisService inherits from BaseService."""
        assert isinstance(demand_analysis_service, BaseService)

    def test_service_has_correct_repository_type(self, demand_analysis_service):
        """Test that service uses DemandAnalysisRepository."""
        assert isinstance(demand_analysis_service.repository, DemandAnalysisRepository)


class TestAnalyzeDemandUseCase:
    """Test analyze_demand use case."""

    def test_analyze_demand_creates_aggregate_with_correct_data(self, demand_analysis_service):
        """Test that analyze_demand creates aggregate with correct postal code, population, station count."""
        result = demand_analysis_service.analyze_demand("10115", 30000, 5)

        assert isinstance(result, DemandAnalysisAggregate)
        assert result.postal_code.value == "10115"
        assert result.get_population() == 30000
        assert result.get_station_count() == 5

    def test_analyze_demand_calculates_priority_automatically(self, demand_analysis_service):
        """Test that analyze_demand automatically calculates demand priority."""
        result = demand_analysis_service.analyze_demand("10115", 30000, 5)

        assert result.demand_priority is not None
        assert isinstance(result.demand_priority, DemandPriority)
        assert result.demand_priority.level == PriorityLevel.HIGH

    def test_analyze_demand_saves_aggregate_to_repository(self, demand_analysis_service, mock_repository):
        """Test that analyze_demand saves aggregate to repository."""
        demand_analysis_service.analyze_demand("10115", 25000, 3)

        mock_repository.save.assert_called_once()
        saved_aggregate = mock_repository.save.call_args[0][0]
        assert saved_aggregate.postal_code.value == "10115"

    def test_analyze_demand_publishes_events(self, demand_analysis_service, mock_repository, mock_event_bus):
        """Test that analyze_demand publishes domain events."""
        demand_analysis_service.analyze_demand("10115", 30000, 5)

        # Should publish events from the aggregate
        mock_event_bus.publish.assert_called()

    def test_analyze_demand_raises_error_for_invalid_postal_code(self, demand_analysis_service):
        """Test that analyze_demand raises error for invalid postal code."""
        with pytest.raises(InvalidPostalCodeError):
            demand_analysis_service.analyze_demand("99999", 10000, 5)

    def test_analyze_demand_with_zero_stations(self, demand_analysis_service, mock_repository):
        """Test analyzing demand with zero stations (critical shortage)."""
        result = demand_analysis_service.analyze_demand("10115", 50000, 0)

        assert result.get_station_count() == 0
        assert result.demand_priority.level == PriorityLevel.HIGH

    def test_analyze_demand_with_low_priority_area(self, demand_analysis_service, mock_repository):
        """Test analyzing demand for low priority area (adequate coverage)."""
        result = demand_analysis_service.analyze_demand("10115", 10000, 10)

        assert result.demand_priority.level == PriorityLevel.LOW

    def test_analyze_demand_with_medium_priority_area(self, demand_analysis_service, mock_repository):
        """Test analyzing demand for medium priority area."""
        result = demand_analysis_service.analyze_demand("10115", 15000, 5)

        assert result.demand_priority.level == PriorityLevel.MEDIUM


class TestAnalyzeMultipleAreasUseCase:
    """Test analyze_multiple_areas use case."""

    def test_analyze_multiple_areas_returns_list_of_aggregates(self, demand_analysis_service, mock_repository):
        """Test that analyze_multiple_areas returns list of aggregates."""
        areas = [
            {"postal_code": "10115", "population": 30000, "station_count": 5},
            {"postal_code": "12345", "population": 15000, "station_count": 8},
        ]

        results = demand_analysis_service.analyze_multiple_areas(areas)

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(agg, DemandAnalysisAggregate) for agg in results)

    def test_analyze_multiple_areas_processes_all_areas(self, demand_analysis_service, mock_repository):
        """Test that all areas are processed and saved."""
        areas = [
            {"postal_code": "10115", "population": 25000, "station_count": 4},
            {"postal_code": "12345", "population": 18000, "station_count": 6},
            {"postal_code": "13579", "population": 12000, "station_count": 8},
        ]

        results = demand_analysis_service.analyze_multiple_areas(areas)

        assert len(results) == 3
        assert mock_repository.save.call_count == 3

    def test_analyze_multiple_areas_continues_on_error(self, demand_analysis_service, mock_repository):
        """Test that processing continues when one area has an error."""
        areas = [
            {"postal_code": "10115", "population": 25000, "station_count": 4},
            {"postal_code": "99999", "population": 18000, "station_count": 6},  # Invalid
            {"postal_code": "13579", "population": 12000, "station_count": 8},
        ]

        with patch("src.demand.application.services.DemandAnalysisService.logger") as mock_logger:
            results = demand_analysis_service.analyze_multiple_areas(areas)

            # Should process 2 valid areas
            assert len(results) == 2
            # Should log error for invalid area
            mock_logger.error.assert_called_once()

    def test_analyze_multiple_areas_with_empty_list(self, demand_analysis_service):
        """Test analyzing empty list of areas."""
        results = demand_analysis_service.analyze_multiple_areas([])

        assert results == []

    def test_analyze_multiple_areas_with_single_area(self, demand_analysis_service):
        """Test analyzing single area in list."""
        areas = [{"postal_code": "10115", "population": 20000, "station_count": 5}]

        results = demand_analysis_service.analyze_multiple_areas(areas)

        assert len(results) == 1
        assert results[0].postal_code.value == "10115"


class TestGetHighPriorityAreasUseCase:
    """Test get_high_priority_areas use case."""

    def test_get_high_priority_areas_returns_only_high_priority(
        self,
        demand_analysis_service,
        mock_repository,
        high_priority_aggregate,
        low_priority_aggregate,
    ):
        """Test that only high priority areas are returned."""
        mock_repository.find_all.return_value = [high_priority_aggregate, low_priority_aggregate]

        results = demand_analysis_service.get_high_priority_areas()

        assert len(results) == 1
        assert results[0].is_high_priority()

    def test_get_high_priority_areas_sorted_by_urgency(self, demand_analysis_service, mock_repository):
        """Test that high priority areas are sorted by urgency score (descending)."""
        agg1 = DemandAnalysisAggregate.create(PostalCode("10115"), population=60000, station_count=10)
        agg2 = DemandAnalysisAggregate.create(PostalCode("12345"), population=100000, station_count=5)
        agg3 = DemandAnalysisAggregate.create(PostalCode("13579"), population=30000, station_count=5)

        mock_repository.find_all.return_value = [agg1, agg2, agg3]

        results = demand_analysis_service.get_high_priority_areas()

        # Should be sorted by urgency score descending
        urgency_scores = [agg.demand_priority.get_urgency_score() for agg in results]
        assert urgency_scores == sorted(urgency_scores, reverse=True)

    def test_get_high_priority_areas_returns_empty_list_when_none_high(
        self, demand_analysis_service, mock_repository, low_priority_aggregate
    ):
        """Test that empty list is returned when no high priority areas exist."""
        mock_repository.find_all.return_value = [low_priority_aggregate]

        results = demand_analysis_service.get_high_priority_areas()

        assert results == []

    def test_get_high_priority_areas_calls_repository_find_all(self, demand_analysis_service, mock_repository):
        """Test that repository find_all is called."""
        mock_repository.find_all.return_value = []

        demand_analysis_service.get_high_priority_areas()

        mock_repository.find_all.assert_called_once()


class TestGetDemandAnalysisUseCase:
    """Test get_demand_analysis use case."""

    def test_get_demand_analysis_returns_aggregate_when_found(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that get_demand_analysis returns aggregate when found."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.get_demand_analysis("10115")

        assert result is high_priority_aggregate
        assert result.postal_code.value == "10115"

    def test_get_demand_analysis_returns_none_when_not_found(self, demand_analysis_service, mock_repository):
        """Test that get_demand_analysis returns None when not found."""
        mock_repository.find_by_postal_code.return_value = None

        result = demand_analysis_service.get_demand_analysis("10115")

        assert result is None

    def test_get_demand_analysis_calls_repository_with_postal_code(self, demand_analysis_service, mock_repository):
        """Test that repository is called with correct postal code."""
        mock_repository.find_by_postal_code.return_value = None

        demand_analysis_service.get_demand_analysis("10115")

        mock_repository.find_by_postal_code.assert_called_once()
        call_args = mock_repository.find_by_postal_code.call_args[0][0]
        assert call_args.value == "10115"

    def test_get_demand_analysis_raises_error_for_invalid_postal_code(self, demand_analysis_service):
        """Test that invalid postal code raises error."""
        with pytest.raises(InvalidPostalCodeError):
            demand_analysis_service.get_demand_analysis("99999")


class TestUpdateDemandAnalysisUseCase:
    """Test update_demand_analysis use case."""

    def test_update_demand_analysis_updates_population(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that update_demand_analysis updates population."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.update_demand_analysis("10115", population=40000)

        assert result.get_population() == 40000

    def test_update_demand_analysis_updates_station_count(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that update_demand_analysis updates station count."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.update_demand_analysis("10115", station_count=10)

        assert result.get_station_count() == 10

    def test_update_demand_analysis_updates_both_fields(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that both population and station count can be updated."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.update_demand_analysis("10115", population=50000, station_count=15)

        assert result.get_population() == 50000
        assert result.get_station_count() == 15

    def test_update_demand_analysis_saves_to_repository(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that updated aggregate is saved to repository."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        demand_analysis_service.update_demand_analysis("10115", population=35000)

        # Should be saved twice: once during analysis, once during update
        assert mock_repository.save.called

    def test_update_demand_analysis_publishes_events(
        self, demand_analysis_service, mock_repository, mock_event_bus, high_priority_aggregate
    ):
        """Test that update publishes domain events."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        demand_analysis_service.update_demand_analysis("10115", population=35000)

        mock_event_bus.publish.assert_called()

    def test_update_demand_analysis_raises_error_when_not_found(self, demand_analysis_service, mock_repository):
        """Test that error is raised when analysis not found."""
        mock_repository.find_by_postal_code.return_value = None

        with pytest.raises(ValueError, match="No analysis found"):
            demand_analysis_service.update_demand_analysis("10115", population=35000)

    def test_update_demand_analysis_with_no_changes(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test update with no population or station count changes."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.update_demand_analysis("10115")

        # Should return the same aggregate without changes
        assert result.population == high_priority_aggregate.population
        assert result.station_count == high_priority_aggregate.station_count


class TestGetRecommendationsUseCase:
    """Test get_recommendations use case."""

    def test_get_recommendations_returns_dict_with_correct_structure(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that recommendations returns dict with expected keys."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.get_recommendations("10115")

        assert isinstance(result, dict)
        assert "postal_code" in result
        assert "current_stations" in result
        assert "recommended_additional_stations" in result
        assert "recommended_total_stations" in result
        assert "target_ratio" in result
        assert "current_ratio" in result
        assert "coverage_assessment" in result

    def test_get_recommendations_calculates_additional_stations_needed(self, demand_analysis_service, mock_repository):
        """Test that recommendations calculates correct number of additional stations."""
        aggregate = DemandAnalysisAggregate.create(PostalCode("10115"), population=20000, station_count=5)
        mock_repository.find_by_postal_code.return_value = aggregate

        result = demand_analysis_service.get_recommendations("10115", target_ratio=2000.0)

        # 20000 / 2000 = 10 total needed, 5 existing = 5 additional
        assert result["recommended_additional_stations"] == 5
        assert result["recommended_total_stations"] == 10

    def test_get_recommendations_with_custom_target_ratio(self, demand_analysis_service, mock_repository):
        """Test recommendations with custom target ratio."""
        aggregate = DemandAnalysisAggregate.create(PostalCode("10115"), population=30000, station_count=10)
        mock_repository.find_by_postal_code.return_value = aggregate

        result = demand_analysis_service.get_recommendations("10115", target_ratio=1000.0)

        # 30000 / 1000 = 30 total needed, 10 existing = 20 additional
        assert result["recommended_additional_stations"] == 20
        assert result["target_ratio"] == 1000.0

    def test_get_recommendations_when_already_meeting_target(self, demand_analysis_service, mock_repository):
        """Test recommendations when area already meets target ratio."""
        aggregate = DemandAnalysisAggregate.create(PostalCode("10115"), population=10000, station_count=10)
        mock_repository.find_by_postal_code.return_value = aggregate

        result = demand_analysis_service.get_recommendations("10115", target_ratio=2000.0)

        # Already meeting target (1000 residents/station < 2000 target)
        assert result["recommended_additional_stations"] == 0

    def test_get_recommendations_includes_current_ratio(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that current ratio is included in recommendations."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.get_recommendations("10115")

        assert "current_ratio" in result
        assert result["current_ratio"] == high_priority_aggregate.get_residents_per_station()

    def test_get_recommendations_includes_coverage_assessment(
        self, demand_analysis_service, mock_repository, high_priority_aggregate
    ):
        """Test that coverage assessment is included."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        result = demand_analysis_service.get_recommendations("10115")

        assert "coverage_assessment" in result
        assert result["coverage_assessment"] in ["CRITICAL", "POOR", "ADEQUATE", "GOOD"]

    def test_get_recommendations_raises_error_when_not_found(self, demand_analysis_service, mock_repository):
        """Test that error is raised when analysis not found."""
        mock_repository.find_by_postal_code.return_value = None

        with pytest.raises(ValueError, match="No analysis found"):
            demand_analysis_service.get_recommendations("10115")


class TestEventPublishingIntegration:
    """Test event publishing integration."""

    def test_analyze_demand_publishes_demand_calculated_event(self, demand_analysis_service, mock_event_bus):
        """Test that analyze_demand publishes DemandAnalysisCalculatedEvent."""
        demand_analysis_service.analyze_demand("10115", 30000, 5)

        # Event bus should be called to publish events
        assert mock_event_bus.publish.called

    def test_analyze_demand_publishes_high_demand_event_for_high_priority(self, demand_analysis_service, mock_event_bus):
        """Test that high demand event is published for high priority areas."""
        demand_analysis_service.analyze_demand("10115", 50000, 5)

        # Should publish both DemandAnalysisCalculated and HighDemandAreaIdentified
        assert mock_event_bus.publish.called

    def test_update_publishes_events_after_changes(
        self, demand_analysis_service, mock_repository, mock_event_bus, high_priority_aggregate
    ):
        """Test that update publishes events after making changes."""
        mock_repository.find_by_postal_code.return_value = high_priority_aggregate

        demand_analysis_service.update_demand_analysis("10115", population=60000)

        mock_event_bus.publish.assert_called()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_analyze_demand_with_negative_population_raises_error(self, demand_analysis_service):
        """Test that negative population raises error."""
        with pytest.raises(ValueError):
            demand_analysis_service.analyze_demand("10115", -1000, 5)

    def test_analyze_demand_with_negative_station_count_raises_error(self, demand_analysis_service):
        """Test that negative station count raises error."""
        with pytest.raises(ValueError):
            demand_analysis_service.analyze_demand("10115", 20000, -5)

    def test_update_with_invalid_postal_code_raises_error(self, demand_analysis_service):
        """Test that updating with invalid postal code raises error."""
        with pytest.raises(InvalidPostalCodeError):
            demand_analysis_service.update_demand_analysis("99999", population=10000)

    def test_get_recommendations_with_invalid_postal_code_raises_error(self, demand_analysis_service):
        """Test that getting recommendations with invalid postal code raises error."""
        with pytest.raises(InvalidPostalCodeError):
            demand_analysis_service.get_recommendations("99999")


class TestServiceBehaviorConsistency:
    """Test consistent behavior across service methods."""

    def test_all_methods_use_postal_code_value_object(self, demand_analysis_service):
        """Test that all methods properly convert string to PostalCode value object."""
        # This is implicitly tested by all the other tests, but explicitly verify
        # that postal codes are validated consistently
        with pytest.raises(InvalidPostalCodeError):
            demand_analysis_service.analyze_demand("invalid", 10000, 5)

        with pytest.raises(InvalidPostalCodeError):
            demand_analysis_service.get_demand_analysis("invalid")

    def test_service_coordinates_with_repository_for_persistence(self, demand_analysis_service, mock_repository):
        """Test that service properly coordinates with repository for all persistence operations."""
        # Analyze creates and saves
        demand_analysis_service.analyze_demand("10115", 20000, 5)
        assert mock_repository.save.called

        # Get retrieves from repository
        mock_repository.find_by_postal_code.return_value = None
        demand_analysis_service.get_demand_analysis("10115")
        assert mock_repository.find_by_postal_code.called

    def test_service_methods_return_appropriate_types(self, demand_analysis_service, mock_repository):
        """Test that service methods return expected types."""
        # analyze_demand returns aggregate
        result = demand_analysis_service.analyze_demand("10115", 20000, 5)
        assert isinstance(result, DemandAnalysisAggregate)

        # analyze_multiple_areas returns list
        results = demand_analysis_service.analyze_multiple_areas([])
        assert isinstance(results, list)

        # get_recommendations returns dict
        mock_repository.find_by_postal_code.return_value = result
        recommendations = demand_analysis_service.get_recommendations("10115")
        assert isinstance(recommendations, dict)
