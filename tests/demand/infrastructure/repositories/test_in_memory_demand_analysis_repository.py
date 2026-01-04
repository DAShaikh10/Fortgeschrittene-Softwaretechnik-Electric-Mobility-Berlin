"""
Unit Tests for InMemoryDemandAnalysisRepository.

Test categories:
- Save operation tests
- Find operations tests (find_by_postal_code, find_all)
- Delete operation tests
- Exists operation tests
- Count operation tests
- Clear operation tests
- Find by priority level tests
- Type validation tests
- Edge cases and boundary values
"""

# pylint: disable=redefined-outer-name

import pytest

from src.shared.domain.value_objects import PostalCode
from src.demand.domain.enums import PriorityLevel
from src.demand.domain.aggregates import DemandAnalysisAggregate
from src.demand.domain.value_objects import DemandPriority, Population, StationCount
from src.demand.infrastructure.repositories import InMemoryDemandAnalysisRepository


@pytest.fixture
def repository():
    """Create a fresh repository for each test."""
    return InMemoryDemandAnalysisRepository()


def create_aggregate(postal_code_str: str, pop_value: int, station_value: int):
    """Helper function to create aggregates with calculated priority."""
    population = Population(pop_value)
    station_count = StationCount(station_value)
    demand_priority = DemandPriority.calculate_priority(population, station_count)
    return DemandAnalysisAggregate(
        postal_code=PostalCode(postal_code_str),
        population=population,
        station_count=station_count,
        demand_priority=demand_priority,
    )


@pytest.fixture
def sample_aggregate():
    """Create a sample demand analysis aggregate."""
    population = Population(30000)
    station_count = StationCount(5)
    demand_priority = DemandPriority.calculate_priority(population, station_count)
    return DemandAnalysisAggregate(
        postal_code=PostalCode("10115"),
        population=population,
        station_count=station_count,
        demand_priority=demand_priority,
    )


@pytest.fixture
def another_aggregate():
    """Create another sample aggregate with different postal code."""
    population = Population(20000)
    station_count = StationCount(10)
    demand_priority = DemandPriority.calculate_priority(population, station_count)
    return DemandAnalysisAggregate(
        postal_code=PostalCode("12345"),
        population=population,
        station_count=station_count,
        demand_priority=demand_priority,
    )


class TestInMemoryDemandAnalysisRepositoryInitialization:
    """Test repository initialization."""

    def test_repository_initialization(self, repository):
        """Test that repository initializes with empty storage."""
        assert repository.count() == 0
        assert repository.find_all() == []

    def test_repository_storage_is_dict(self, repository):
        """Test that internal storage is a dictionary."""
        assert hasattr(repository, "_storage")
        # pylint: disable=protected-access
        assert isinstance(repository._storage, dict)


class TestSaveOperation:
    """Test save operation."""

    def test_save_aggregate(self, repository, sample_aggregate):
        """Test saving a demand analysis aggregate."""
        repository.save(sample_aggregate)

        assert repository.count() == 1
        assert repository.exists(PostalCode("10115"))

    def test_save_multiple_aggregates(self, repository, sample_aggregate, another_aggregate):
        """Test saving multiple aggregates."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)

        assert repository.count() == 2

    def test_save_updates_existing_aggregate(self, repository):
        """Test that saving with same postal code updates the aggregate."""
        aggregate1 = create_aggregate("10115", 30000, 5)
        repository.save(aggregate1)

        # Save another aggregate with same postal code
        aggregate2 = create_aggregate("10115", 50000, 10)
        repository.save(aggregate2)

        # Should still have only 1 aggregate (updated)
        assert repository.count() == 1
        found = repository.find_by_postal_code(PostalCode("10115"))
        assert found.get_population() == 50000

    def test_save_invalid_type_raises_type_error(self, repository):
        """Test that saving non-aggregate raises TypeError."""
        with pytest.raises(TypeError, match="Must be a DemandAnalysisAggregate"):
            repository.save("not an aggregate")

    def test_save_none_raises_type_error(self, repository):
        """Test that saving None raises TypeError."""
        with pytest.raises(TypeError, match="Must be a DemandAnalysisAggregate"):
            repository.save(None)


class TestFindByPostalCode:
    """Test find_by_postal_code operation."""

    def test_find_existing_aggregate(self, repository, sample_aggregate):
        """Test finding an existing aggregate by postal code."""
        repository.save(sample_aggregate)

        found = repository.find_by_postal_code(PostalCode("10115"))

        assert found is not None
        assert found.postal_code.value == "10115"
        assert found.get_population() == 30000

    def test_find_non_existing_aggregate_returns_none(self, repository):
        """Test that finding non-existing aggregate returns None."""
        found = repository.find_by_postal_code(PostalCode("14000"))

        assert found is None

    def test_find_with_invalid_type_raises_type_error(self, repository):
        """Test that finding with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="postal_code must be a PostalCode value object"):
            repository.find_by_postal_code("10115")

    def test_find_after_multiple_saves(self, repository, sample_aggregate, another_aggregate):
        """Test finding specific aggregate after saving multiple."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)

        found = repository.find_by_postal_code(PostalCode("12345"))

        assert found is not None
        assert found.postal_code.value == "12345"


class TestFindAll:
    """Test find_all operation."""

    def test_find_all_empty_repository(self, repository):
        """Test find_all on empty repository."""
        results = repository.find_all()

        assert results == []
        assert len(results) == 0

    def test_find_all_single_aggregate(self, repository, sample_aggregate):
        """Test find_all with single aggregate."""
        repository.save(sample_aggregate)

        results = repository.find_all()

        assert len(results) == 1
        assert results[0].postal_code.value == "10115"

    def test_find_all_multiple_aggregates(self, repository, sample_aggregate, another_aggregate):
        """Test find_all with multiple aggregates."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)

        results = repository.find_all()

        assert len(results) == 2
        postal_codes = [agg.postal_code.value for agg in results]
        assert "10115" in postal_codes
        assert "12345" in postal_codes

    def test_find_all_returns_list(self, repository, sample_aggregate):
        """Test that find_all returns a list."""
        repository.save(sample_aggregate)

        results = repository.find_all()

        assert isinstance(results, list)


class TestDeleteOperation:
    """Test delete operation."""

    def test_delete_existing_aggregate(self, repository, sample_aggregate):
        """Test deleting an existing aggregate."""
        repository.save(sample_aggregate)

        result = repository.delete(PostalCode("10115"))

        assert result is True
        assert repository.count() == 0
        assert not repository.exists(PostalCode("10115"))

    def test_delete_non_existing_aggregate(self, repository):
        """Test deleting non-existing aggregate returns False."""
        result = repository.delete(PostalCode("14000"))

        assert result is False

    def test_delete_with_invalid_type_raises_type_error(self, repository):
        """Test that delete with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="postal_code must be a PostalCode value object"):
            repository.delete("10115")

    def test_delete_one_of_multiple(self, repository, sample_aggregate, another_aggregate):
        """Test deleting one aggregate when multiple exist."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)

        result = repository.delete(PostalCode("10115"))

        assert result is True
        assert repository.count() == 1
        assert not repository.exists(PostalCode("10115"))
        assert repository.exists(PostalCode("12345"))


class TestExistsOperation:
    """Test exists operation."""

    def test_exists_returns_true_for_existing_aggregate(self, repository, sample_aggregate):
        """Test exists returns True for existing aggregate."""
        repository.save(sample_aggregate)

        assert repository.exists(PostalCode("10115")) is True

    def test_exists_returns_false_for_non_existing_aggregate(self, repository):
        """Test exists returns False for non-existing aggregate."""
        assert repository.exists(PostalCode("14000")) is False

    def test_exists_with_invalid_type_raises_type_error(self, repository):
        """Test that exists with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="postal_code must be a PostalCode value object"):
            repository.exists("10115")

    def test_exists_after_delete(self, repository, sample_aggregate):
        """Test exists returns False after deleting aggregate."""
        repository.save(sample_aggregate)
        repository.delete(PostalCode("10115"))

        assert repository.exists(PostalCode("10115")) is False


class TestCountOperation:
    """Test count operation."""

    def test_count_empty_repository(self, repository):
        """Test count on empty repository."""
        assert repository.count() == 0

    def test_count_single_aggregate(self, repository, sample_aggregate):
        """Test count with single aggregate."""
        repository.save(sample_aggregate)

        assert repository.count() == 1

    def test_count_multiple_aggregates(self, repository, sample_aggregate, another_aggregate):
        """Test count with multiple aggregates."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)

        assert repository.count() == 2

    def test_count_after_delete(self, repository, sample_aggregate, another_aggregate):
        """Test count after deleting an aggregate."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)
        repository.delete(PostalCode("10115"))

        assert repository.count() == 1

    def test_count_after_update(self, repository):
        """Test that count doesn't increase on update."""
        aggregate1 = create_aggregate("10115", 30000, 5)
        repository.save(aggregate1)

        aggregate2 = create_aggregate("10115", 50000, 10)
        repository.save(aggregate2)

        assert repository.count() == 1


class TestClearOperation:
    """Test clear operation."""

    def test_clear_empty_repository(self, repository):
        """Test clearing empty repository."""
        repository.clear()

        assert repository.count() == 0

    def test_clear_removes_all_aggregates(self, repository, sample_aggregate, another_aggregate):
        """Test that clear removes all aggregates."""
        repository.save(sample_aggregate)
        repository.save(another_aggregate)

        repository.clear()

        assert repository.count() == 0
        assert repository.find_all() == []
        assert not repository.exists(PostalCode("10115"))
        assert not repository.exists(PostalCode("12345"))

    def test_clear_allows_new_saves(self, repository, sample_aggregate, another_aggregate):
        """Test that repository can be used after clearing."""
        repository.save(sample_aggregate)
        repository.clear()
        repository.save(another_aggregate)

        assert repository.count() == 1
        assert repository.exists(PostalCode("12345"))


class TestFindByPriorityLevel:
    """Test find_by_priority_level operation."""

    def test_find_by_priority_level_high(self, repository):
        """Test finding aggregates with HIGH priority."""
        high_priority_agg = create_aggregate("10115", 30000, 5)  # 6000 residents/station = HIGH
        repository.save(high_priority_agg)

        results = repository.find_by_priority_level("High")

        assert len(results) == 1
        assert results[0].demand_priority.level == PriorityLevel.HIGH

    def test_find_by_priority_level_medium(self, repository):
        """Test finding aggregates with MEDIUM priority."""
        medium_priority_agg = create_aggregate("10115", 15000, 5)  # 3000 residents/station = MEDIUM
        repository.save(medium_priority_agg)

        results = repository.find_by_priority_level("Medium")

        assert len(results) == 1
        assert results[0].demand_priority.level == PriorityLevel.MEDIUM

    def test_find_by_priority_level_low(self, repository):
        """Test finding aggregates with LOW priority."""
        low_priority_agg = create_aggregate("10115", 10000, 10)  # 1000 residents/station = LOW
        repository.save(low_priority_agg)

        results = repository.find_by_priority_level("Low")

        assert len(results) == 1
        assert results[0].demand_priority.level == PriorityLevel.LOW

    def test_find_by_priority_level_multiple_matches(self, repository):
        """Test finding multiple aggregates with same priority."""
        agg1 = create_aggregate("10115", 30000, 5)
        agg2 = create_aggregate("12345", 40000, 6)
        repository.save(agg1)
        repository.save(agg2)

        results = repository.find_by_priority_level("High")

        assert len(results) == 2

    def test_find_by_priority_level_no_matches(self, repository):
        """Test finding with no matching priority level."""
        low_priority_agg = create_aggregate("10115", 10000, 10)
        repository.save(low_priority_agg)

        results = repository.find_by_priority_level("High")

        assert len(results) == 0


class TestRepositoryIntegration:
    """Integration tests for repository operations."""

    def test_complete_crud_workflow(self, repository):
        """Test complete Create-Read-Update-Delete workflow."""
        # Create
        aggregate = create_aggregate("10115", 30000, 5)
        repository.save(aggregate)
        assert repository.count() == 1

        # Read
        found = repository.find_by_postal_code(PostalCode("10115"))
        assert found is not None
        assert found.get_population() == 30000

        # Update
        updated_aggregate = create_aggregate("10115", 50000, 10)
        repository.save(updated_aggregate)
        assert repository.count() == 1  # Still just one
        found = repository.find_by_postal_code(PostalCode("10115"))
        assert found.get_population() == 50000

        # Delete
        result = repository.delete(PostalCode("10115"))
        assert result is True
        assert repository.count() == 0

    def test_repository_isolation(self):
        """Test that separate repository instances are isolated."""
        repo1 = InMemoryDemandAnalysisRepository()
        repo2 = InMemoryDemandAnalysisRepository()

        aggregate = create_aggregate("10115", 30000, 5)
        repo1.save(aggregate)

        assert repo1.count() == 1
        assert repo2.count() == 0

    def test_repository_with_different_priority_aggregates(self, repository):
        """Test repository with aggregates of different priorities."""
        high_priority = create_aggregate("10115", 30000, 5)
        medium_priority = create_aggregate("12345", 15000, 5)
        low_priority = create_aggregate("13579", 10000, 10)

        repository.save(high_priority)
        repository.save(medium_priority)
        repository.save(low_priority)

        assert repository.count() == 3
        assert len(repository.find_by_priority_level("High")) == 1
        assert len(repository.find_by_priority_level("Medium")) == 1
        assert len(repository.find_by_priority_level("Low")) == 1
