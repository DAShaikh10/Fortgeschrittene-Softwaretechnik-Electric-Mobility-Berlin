"""
Unit Tests for DemandPriority Value Object.

Test categories:
- Validation tests (invariants)
- Factory method tests (calculate_priority)
- Business logic tests (is_high_priority, get_urgency_score)
- Edge cases and boundary values
- Invalid inputs
"""

import pytest

from src.demand.application.enums import PriorityLevel
from src.demand.domain.value_objects import DemandPriority


class TestDemandPriorityValidation:
    """Test validation logic in __post_init__."""

    def test_valid_demand_priority_creation(self):
        """Test creating a valid DemandPriority instance."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)

        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == 6000.0

    def test_invalid_priority_level_raises_value_error(self):
        """Test that invalid priority level type raises ValueError."""
        with pytest.raises(ValueError, match="Level must be a PriorityLevel enum value"):
            DemandPriority(level="HIGH", residents_per_station=5000.0)

    def test_negative_residents_per_station_raises_value_error(self):
        """Test that negative residents per station raises ValueError."""
        with pytest.raises(ValueError, match="Residents per station cannot be negative"):
            DemandPriority(level=PriorityLevel.LOW, residents_per_station=-100.0)

    def test_zero_residents_per_station_is_valid(self):
        """Test that zero residents per station is valid."""
        priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=0.0)

        assert priority.residents_per_station == 0.0


class TestDemandPriorityCalculation:
    """Test calculate_priority static factory method."""

    def test_high_priority_calculation_above_threshold(self):
        """Test HIGH priority when residents/station > 5000."""
        priority = DemandPriority.calculate_priority(population=15000, station_count=2)

        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == 7500.0

    def test_high_priority_at_exact_boundary(self):
        """Test HIGH priority at exactly 5001 residents/station."""
        priority = DemandPriority.calculate_priority(population=5001, station_count=1)

        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == 5001.0

    def test_medium_priority_calculation_in_range(self):
        """Test MEDIUM priority when 2000 < residents/station <= 5000."""
        priority = DemandPriority.calculate_priority(population=10000, station_count=3)

        assert priority.level == PriorityLevel.MEDIUM
        assert priority.residents_per_station == pytest.approx(3333.33, rel=0.01)

    def test_medium_priority_at_upper_boundary(self):
        """Test MEDIUM priority at exactly 5000 residents/station."""
        priority = DemandPriority.calculate_priority(population=5000, station_count=1)

        assert priority.level == PriorityLevel.MEDIUM
        assert priority.residents_per_station == 5000.0

    def test_medium_priority_at_lower_boundary(self):
        """Test MEDIUM priority at exactly 2001 residents/station."""
        priority = DemandPriority.calculate_priority(population=2001, station_count=1)

        assert priority.level == PriorityLevel.MEDIUM
        assert priority.residents_per_station == 2001.0

    def test_low_priority_calculation_below_threshold(self):
        """Test LOW priority when residents/station <= 2000."""
        priority = DemandPriority.calculate_priority(population=4000, station_count=3)

        assert priority.level == PriorityLevel.LOW
        assert priority.residents_per_station == pytest.approx(1333.33, rel=0.01)

    def test_low_priority_at_exact_boundary(self):
        """Test LOW priority at exactly 2000 residents/station."""
        priority = DemandPriority.calculate_priority(population=2000, station_count=1)

        assert priority.level == PriorityLevel.LOW
        assert priority.residents_per_station == 2000.0

    def test_zero_stations_returns_high_priority(self):
        """Test that zero stations always returns HIGH priority with population as ratio."""
        priority = DemandPriority.calculate_priority(population=10000, station_count=0)

        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == 10000.0

    def test_zero_population_zero_stations(self):
        """Test edge case: zero population and zero stations."""
        priority = DemandPriority.calculate_priority(population=0, station_count=0)

        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == 0.0

    def test_zero_population_with_stations(self):
        """Test edge case: zero population with existing stations."""
        priority = DemandPriority.calculate_priority(population=0, station_count=5)

        assert priority.level == PriorityLevel.LOW
        assert priority.residents_per_station == 0.0

    def test_large_population_calculation(self):
        """Test with large population numbers."""
        priority = DemandPriority.calculate_priority(population=1000000, station_count=50)

        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == 20000.0


class TestDemandPriorityBusinessLogic:
    """Test business logic methods."""

    def test_is_high_priority_returns_true_for_high(self):
        """Test is_high_priority returns True for HIGH priority."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)

        assert priority.is_high_priority() is True

    def test_is_high_priority_returns_false_for_medium(self):
        """Test is_high_priority returns False for MEDIUM priority."""
        priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3000.0)

        assert priority.is_high_priority() is False

    def test_is_high_priority_returns_false_for_low(self):
        """Test is_high_priority returns False for LOW priority."""
        priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=1000.0)

        assert priority.is_high_priority() is False


class TestDemandPriorityUrgencyScore:
    """Test urgency score calculation."""

    def test_urgency_score_critical_above_10000(self):
        """Test urgency score of 100 for critical shortage (≥10,000 residents/station)."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=15000.0)

        assert priority.get_urgency_score() == 100.0

    def test_urgency_score_critical_at_exact_boundary(self):
        """Test urgency score of 100 at exactly 10,000 residents/station."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=10000.0)

        assert priority.get_urgency_score() == 100.0

    def test_urgency_score_high_between_5000_and_10000(self):
        """Test urgency score of 75 for high demand (5,000-9,999 residents/station)."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=7500.0)

        assert priority.get_urgency_score() == 75.0

    def test_urgency_score_high_at_exact_boundary(self):
        """Test urgency score of 75 at exactly 5,000 residents/station."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=5000.0)

        assert priority.get_urgency_score() == 75.0

    def test_urgency_score_medium_between_2000_and_5000(self):
        """Test urgency score of 50 for medium demand (2,000-4,999 residents/station)."""
        priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3500.0)

        assert priority.get_urgency_score() == 50.0

    def test_urgency_score_medium_at_exact_boundary(self):
        """Test urgency score of 50 at exactly 2,000 residents/station."""
        priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=2000.0)

        assert priority.get_urgency_score() == 50.0

    def test_urgency_score_low_below_2000(self):
        """Test urgency score of 25 for adequate coverage (<2,000 residents/station)."""
        priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=1500.0)

        assert priority.get_urgency_score() == 25.0

    def test_urgency_score_low_at_zero(self):
        """Test urgency score of 25 at 0 residents/station."""
        priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=0.0)

        assert priority.get_urgency_score() == 25.0


class TestDemandPriorityStringRepresentation:
    """Test string representation."""

    def test_string_representation_high_priority(self):
        """Test string representation for HIGH priority."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6543.21)

        assert str(priority) == "High (6543 residents/station)"

    def test_string_representation_medium_priority(self):
        """Test string representation for MEDIUM priority."""
        priority = DemandPriority(level=PriorityLevel.MEDIUM, residents_per_station=3456.78)

        assert str(priority) == "Medium (3457 residents/station)"

    def test_string_representation_low_priority(self):
        """Test string representation for LOW priority."""
        priority = DemandPriority(level=PriorityLevel.LOW, residents_per_station=1234.56)

        assert str(priority) == "Low (1235 residents/station)"


class TestDemandPriorityImmutability:
    """Test immutability of DemandPriority (frozen dataclass)."""

    def test_cannot_modify_level(self):
        """Test that level attribute cannot be modified."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)

        with pytest.raises(AttributeError):
            priority.level = PriorityLevel.LOW

    def test_cannot_modify_residents_per_station(self):
        """Test that residents_per_station attribute cannot be modified."""
        priority = DemandPriority(level=PriorityLevel.HIGH, residents_per_station=6000.0)

        with pytest.raises(AttributeError):
            priority.residents_per_station = 1000.0


class TestDemandPriorityIntegration:
    """Integration tests combining multiple methods."""

    def test_full_workflow_high_priority_area(self):
        """Test complete workflow for a high priority area."""
        # Calculate priority for area with shortage
        priority = DemandPriority.calculate_priority(population=25000, station_count=3)

        # Verify classification
        assert priority.level == PriorityLevel.HIGH
        assert priority.residents_per_station == pytest.approx(8333.33, rel=0.01)

        # Verify business logic
        assert priority.is_high_priority() is True
        assert priority.get_urgency_score() == 75.0

        # Verify string representation
        assert "High" in str(priority)
        assert "8333" in str(priority)

    def test_full_workflow_medium_priority_area(self):
        """Test complete workflow for a medium priority area."""
        # Calculate priority for area with moderate coverage
        priority = DemandPriority.calculate_priority(population=12000, station_count=4)

        # Verify classification
        assert priority.level == PriorityLevel.MEDIUM
        assert priority.residents_per_station == 3000.0

        # Verify business logic
        assert priority.is_high_priority() is False
        assert priority.get_urgency_score() == 50.0

        # Verify string representation
        assert "Medium" in str(priority)
        assert "3000" in str(priority)

    def test_full_workflow_low_priority_area(self):
        """Test complete workflow for a low priority area."""
        # Calculate priority for area with good coverage
        priority = DemandPriority.calculate_priority(population=5000, station_count=5)

        # Verify classification
        assert priority.level == PriorityLevel.LOW
        assert priority.residents_per_station == 1000.0

        # Verify business logic
        assert priority.is_high_priority() is False
        assert priority.get_urgency_score() == 25.0

        # Verify string representation
        assert "Low" in str(priority)
        assert "1000" in str(priority)
