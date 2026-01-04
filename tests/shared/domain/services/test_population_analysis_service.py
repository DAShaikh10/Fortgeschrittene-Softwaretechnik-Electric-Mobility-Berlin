"""
Unit Tests for PopulationAnalysisService.

Test categories:
- Density categorization logic
- High density checks
- Demand ratio calculations
"""

import pytest
from src.shared.domain.services import PopulationAnalysisService

class TestDensityCategory:
    """Test get_density_category business logic."""

    def test_high_density_category(self):
        """Test HIGH category for population > 20,000."""
        assert PopulationAnalysisService.get_density_category(25000) == "HIGH"
        assert PopulationAnalysisService.get_density_category(20001) == "HIGH"

    def test_medium_density_category(self):
        """Test MEDIUM category (10,000 - 20,000)."""
        assert PopulationAnalysisService.get_density_category(20000) == "MEDIUM"
        assert PopulationAnalysisService.get_density_category(15000) == "MEDIUM"
        assert PopulationAnalysisService.get_density_category(10001) == "MEDIUM"

    def test_low_density_category(self):
        """Test LOW category (< 10,000)."""
        assert PopulationAnalysisService.get_density_category(10000) == "LOW"
        assert PopulationAnalysisService.get_density_category(5000) == "LOW"
        assert PopulationAnalysisService.get_density_category(0) == "LOW"

class TestHighDensityCheck:
    """Test is_high_density business rule."""

    def test_is_high_density(self):
        """Test high density returns True for population > 15,000."""
        assert PopulationAnalysisService.is_high_density(20000) is True
        assert PopulationAnalysisService.is_high_density(15001) is True

    def test_is_not_high_density(self):
        """Test not high density for population <= 15,000."""
        assert PopulationAnalysisService.is_high_density(15000) is False
        assert PopulationAnalysisService.is_high_density(10000) is False
        assert PopulationAnalysisService.is_high_density(0) is False

class TestDemandRatioCalculation:
    """Test calculate_demand_ratio business calculation."""

    def test_demand_ratio_with_stations(self):
        """Test calculation with normal inputs."""
        # 30,000 people / 5 stations = 6000
        assert PopulationAnalysisService.calculate_demand_ratio(30000, 5) == 6000.0

    def test_demand_ratio_zero_stations(self):
        """Test division by zero protection (should use 1)."""
        # 25,000 people / max(0, 1) = 25,000
        assert PopulationAnalysisService.calculate_demand_ratio(25000, 0) == 25000.0

    def test_demand_ratio_fractional(self):
        """Test fractional results."""
        # 10,000 / 3 = 3333.33...
        ratio = PopulationAnalysisService.calculate_demand_ratio(10000, 3)
        assert ratio == pytest.approx(3333.33, rel=0.01)

class TestServiceIntegration:
    """Integration style tests for the service logic."""

    def test_high_density_correlation(self):
        """Test logic correlation: 16k pop is High Density but Medium Category."""
        population = 16000
        is_high = PopulationAnalysisService.is_high_density(population)
        category = PopulationAnalysisService.get_density_category(population)

        assert is_high is True
        assert category == "MEDIUM"