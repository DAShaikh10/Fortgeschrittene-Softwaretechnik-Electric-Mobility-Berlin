"""
Unit Tests for PowerCapacityDTO.

Test categories:
- DTO creation and attributes
- to_dict() method
- Immutability
"""

import dataclasses

from src.shared.application.dtos import PowerCapacityDTO


class TestPowerCapacityDTOCreation:
    """Test PowerCapacityDTO creation and basic attributes."""

    def test_create_dto_with_all_attributes(self):
        """Test creating DTO with all attributes."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=150.0, station_count=5, capacity_category="High")

        assert dto.postal_code == "10115"
        assert dto.total_capacity_kw == 150.0
        assert dto.station_count == 5
        assert dto.capacity_category == "High"

    def test_create_dto_without_category(self):
        """Test creating DTO without capacity_category."""
        dto = PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2)

        assert dto.postal_code == "10117"
        assert dto.total_capacity_kw == 50.0
        assert dto.station_count == 2
        assert dto.capacity_category is None

    def test_create_dto_with_zero_values(self):
        """Test creating DTO with zero values."""
        dto = PowerCapacityDTO(postal_code="10119", total_capacity_kw=0.0, station_count=0)

        assert dto.total_capacity_kw == 0.0
        assert dto.station_count == 0


class TestPowerCapacityDTOToDictMethod:
    """Test to_dict() method functionality."""

    def test_to_dict_with_category(self):
        """Test to_dict() includes capacity_category when present."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=150.0, station_count=5, capacity_category="High")

        result = dto.to_dict()

        assert isinstance(result, dict)
        assert result["postal_code"] == "10115"
        assert result["total_capacity_kw"] == 150.0
        assert result["station_count"] == 5
        assert result["capacity_category"] == "High"
        assert len(result) == 4

    def test_to_dict_without_category(self):
        """Test to_dict() excludes capacity_category when None."""
        dto = PowerCapacityDTO(postal_code="10117", total_capacity_kw=50.0, station_count=2)

        result = dto.to_dict()

        assert isinstance(result, dict)
        assert result["postal_code"] == "10117"
        assert result["total_capacity_kw"] == 50.0
        assert result["station_count"] == 2
        assert "capacity_category" not in result
        assert len(result) == 3

    def test_to_dict_with_none_category_explicitly(self):
        """Test to_dict() with capacity_category explicitly set to None."""
        dto = PowerCapacityDTO(postal_code="10119", total_capacity_kw=75.0, station_count=3, capacity_category=None)

        result = dto.to_dict()

        assert "capacity_category" not in result
        assert len(result) == 3

    def test_to_dict_with_zero_values(self):
        """Test to_dict() with zero values."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=0.0, station_count=0, capacity_category="None")

        result = dto.to_dict()

        assert result["total_capacity_kw"] == 0.0
        assert result["station_count"] == 0
        assert result["capacity_category"] == "None"

    def test_to_dict_returns_new_dict_each_time(self):
        """Test that to_dict() returns a new dictionary each time."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=100.0, station_count=4)

        result1 = dto.to_dict()
        result2 = dto.to_dict()

        assert result1 == result2
        assert result1 is not result2  # Different objects


class TestPowerCapacityDTOImmutability:
    """Test that PowerCapacityDTO is immutable (frozen dataclass)."""

    def test_dto_is_frozen(self):
        """Test that DTO is a frozen dataclass."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=150.0, station_count=5)

        assert dataclasses.is_dataclass(dto)
        # Check that the dataclass is frozen
        assert dto.__dataclass_params__.frozen is True

    def test_dto_attributes_immutable(self):
        """Test that attempting to modify attributes raises error."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=150.0, station_count=5)

        try:
            dto.postal_code = "10117"  # type: ignore
            assert False, "Should have raised FrozenInstanceError"
        except dataclasses.FrozenInstanceError:
            pass  # Expected


class TestPowerCapacityDTOEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_dto_with_large_capacity(self):
        """Test DTO with large capacity value."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=999999.99, station_count=1000)

        result = dto.to_dict()
        assert result["total_capacity_kw"] == 999999.99
        assert result["station_count"] == 1000

    def test_dto_with_fractional_capacity(self):
        """Test DTO with fractional capacity value."""
        dto = PowerCapacityDTO(postal_code="10115", total_capacity_kw=123.456, station_count=7)

        result = dto.to_dict()
        assert result["total_capacity_kw"] == 123.456

    def test_dto_with_all_category_types(self):
        """Test DTO with different category values."""
        categories = ["None", "Low", "Medium", "High"]

        for category in categories:
            dto = PowerCapacityDTO(
                postal_code="10115", total_capacity_kw=50.0, station_count=2, capacity_category=category
            )
            result = dto.to_dict()
            assert result["capacity_category"] == category
