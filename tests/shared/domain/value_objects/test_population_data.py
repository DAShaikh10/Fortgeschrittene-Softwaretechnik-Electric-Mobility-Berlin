"""
Unit Tests for PopulationData Value Object.

Test categories:
- Validation tests (invariants)
- Immutability tests
- Equality tests
"""
import pytest
from src.shared.domain.value_objects import PopulationData, PostalCode

@pytest.fixture
def valid_postal_code():
    return PostalCode("10115")

@pytest.fixture
def another_postal_code():
    return PostalCode("12045")

class TestPopulationDataValidation:
    """Test validation logic in __post_init__."""

    def test_valid_population_data_creation(self, valid_postal_code):
        pop_data = PopulationData(postal_code=valid_postal_code, population=30000)
        assert pop_data.postal_code == valid_postal_code
        assert pop_data.population == 30000

    def test_zero_population_is_valid(self, valid_postal_code):
        pop_data = PopulationData(postal_code=valid_postal_code, population=0)
        assert pop_data.population == 0

    def test_negative_population_raises_value_error(self, valid_postal_code):
        with pytest.raises(ValueError, match="Population cannot be negative"):
            PopulationData(postal_code=valid_postal_code, population=-1000)

class TestPopulationDataGetPopulation:
    """Test get_population query method."""

    def test_get_population_returns_correct_value(self, valid_postal_code):
        pop_data = PopulationData(postal_code=valid_postal_code, population=30000)
        assert pop_data.get_population() == 30000

class TestPopulationDataImmutability:
    """Test immutability of PopulationData."""

    def test_cannot_modify_population(self, valid_postal_code):
        pop_data = PopulationData(postal_code=valid_postal_code, population=30000)
        with pytest.raises(AttributeError):
            pop_data.population = 50000

class TestPopulationDataEquality:
    """Test equality and comparison."""

    def test_equality(self, valid_postal_code, another_postal_code):
        p1 = PopulationData(valid_postal_code, 100)
        p2 = PopulationData(valid_postal_code, 100)
        p3 = PopulationData(valid_postal_code, 200)
        p4 = PopulationData(another_postal_code, 100)

        assert p1 == p2
        assert p1 != p3
        assert p1 != p4

class TestPopulationDataRepr:
    """Test string representation."""

    def test_repr_contains_data(self, valid_postal_code):
        pop_data = PopulationData(postal_code=valid_postal_code, population=30000)
        assert "30000" in repr(pop_data)
        assert "10115" in repr(pop_data)