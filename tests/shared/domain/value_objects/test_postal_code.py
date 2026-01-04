"""
Unit Tests for PostalCode Value Object.

Test categories:
- Validation tests (invariants)
- Business rules (Berlin-specific postal codes)
- Static methods (get_values)
- Immutability tests
- Edge cases and boundary values
"""

# pylint: disable=redefined-outer-name  # pytest fixtures redefine names

import pytest

from src.shared.domain.value_objects import PostalCode
from src.shared.domain.exceptions import InvalidPostalCodeError


class TestPostalCodeValidation:
    """Test validation logic in __post_init__."""

    def test_valid_postal_code_starting_with_10(self):
        """Test creating a valid postal code starting with 10."""
        postal_code = PostalCode("10115")

        assert postal_code.value == "10115"

    def test_valid_postal_code_starting_with_12(self):
        """Test creating a valid postal code starting with 12."""
        postal_code = PostalCode("12045")

        assert postal_code.value == "12045"

    def test_valid_postal_code_starting_with_13(self):
        """Test creating a valid postal code starting with 13."""
        postal_code = PostalCode("13353")

        assert postal_code.value == "13353"

    def test_valid_postal_code_starting_with_14(self):
        """Test creating a valid postal code starting with 14."""
        postal_code = PostalCode("14199")

        assert postal_code.value == "14199"

    def test_postal_code_with_leading_whitespace(self):
        """Test that leading whitespace is stripped."""
        postal_code = PostalCode("  10115")

        assert postal_code.value == "10115"

    def test_postal_code_with_trailing_whitespace(self):
        """Test that trailing whitespace is stripped."""
        postal_code = PostalCode("10115  ")

        assert postal_code.value == "10115"

    def test_postal_code_with_surrounding_whitespace(self):
        """Test that surrounding whitespace is stripped."""
        postal_code = PostalCode("  10115  ")

        assert postal_code.value == "10115"

    def test_none_postal_code_raises_error(self):
        """Test that None value raises InvalidPostalCodeError."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code cannot be None or empty"):
            PostalCode(None)

    def test_empty_string_postal_code_raises_error(self):
        """Test that empty string raises InvalidPostalCodeError."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code cannot be None or empty"):
            PostalCode("")

    def test_whitespace_only_postal_code_raises_error(self):
        """Test that whitespace-only string raises InvalidPostalCodeError."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code cannot be None or empty"):
            PostalCode("   ")

    def test_non_numeric_postal_code_raises_error(self):
        """Test that non-numeric postal code raises InvalidPostalCodeError."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code must be numeric"):
            PostalCode("1011A")

    def test_alphabetic_postal_code_raises_error(self):
        """Test that alphabetic postal code raises InvalidPostalCodeError."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code must be numeric"):
            PostalCode("ABCDE")

    def test_postal_code_with_special_characters_raises_error(self):
        """Test that postal code with special characters raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code must be numeric"):
            PostalCode("10-115")

    def test_too_short_postal_code_raises_error(self):
        """Test that postal code with less than 5 digits raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code must be exactly 5 digits"):
            PostalCode("1011")

    def test_too_long_postal_code_raises_error(self):
        """Test that postal code with more than 5 digits raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code must be exactly 5 digits"):
            PostalCode("101156")

    def test_single_digit_postal_code_raises_error(self):
        """Test that single digit postal code raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Postal code must be exactly 5 digits"):
            PostalCode("1")


class TestPostalCodeBerlinSpecificRules:
    """Test Berlin-specific postal code rules."""

    def test_postal_code_starting_with_11_raises_error(self):
        """Test that postal code starting with 11 raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("11000")

    def test_postal_code_starting_with_15_raises_error(self):
        """Test that postal code starting with 15 raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("15000")

    def test_postal_code_starting_with_20_raises_error(self):
        """Test that postal code starting with 20 raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("20000")

    def test_postal_code_starting_with_00_raises_error(self):
        """Test that postal code starting with 00 raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("00000")

    def test_postal_code_at_lower_boundary_10001(self):
        """Test postal code at lower boundary (10001)."""
        postal_code = PostalCode("10001")

        assert postal_code.value == "10001"

    def test_postal_code_at_upper_boundary_14199(self):
        """Test postal code at upper boundary (14199)."""
        postal_code = PostalCode("14199")

        assert postal_code.value == "14199"

    def test_postal_code_below_lower_boundary_10000_raises_error(self):
        """Test that 10000 (at boundary) raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("10000")

    def test_postal_code_above_upper_boundary_14200_raises_error(self):
        """Test that 14200 (at boundary) raises error."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("14200")

    def test_postal_code_14999_raises_error(self):
        """Test that 14999 raises error (above valid range)."""
        with pytest.raises(InvalidPostalCodeError, match="Berlin postal code must start with 10, 12, 13, or 14"):
            PostalCode("14999")


class TestPostalCodeGetValues:
    """Test get_values static method."""

    def test_get_values_with_multiple_postal_codes(self):
        """Test get_values returns list of string values."""
        postal_codes = [PostalCode("10115"), PostalCode("12045"), PostalCode("13353")]

        values = PostalCode.get_values(postal_codes)

        assert values == ["10115", "12045", "13353"]

    def test_get_values_with_single_postal_code(self):
        """Test get_values with single postal code."""
        postal_codes = [PostalCode("10115")]

        values = PostalCode.get_values(postal_codes)

        assert values == ["10115"]

    def test_get_values_with_empty_list(self):
        """Test get_values with empty list."""
        postal_codes = []

        values = PostalCode.get_values(postal_codes)

        assert values == []

    def test_get_values_preserves_order(self):
        """Test that get_values preserves the order of postal codes."""
        postal_codes = [PostalCode("14199"), PostalCode("10115"), PostalCode("13353"), PostalCode("12045")]

        values = PostalCode.get_values(postal_codes)

        assert values == ["14199", "10115", "13353", "12045"]

    def test_get_values_with_duplicate_postal_codes(self):
        """Test get_values with duplicate postal codes."""
        postal_codes = [PostalCode("10115"), PostalCode("10115"), PostalCode("12045")]

        values = PostalCode.get_values(postal_codes)

        assert values == ["10115", "10115", "12045"]


class TestPostalCodeImmutability:
    """Test immutability of PostalCode (frozen dataclass)."""

    def test_cannot_modify_value(self):
        """Test that value attribute cannot be modified."""
        postal_code = PostalCode("10115")

        with pytest.raises(AttributeError):
            postal_code.value = "12045"


class TestPostalCodeEquality:
    """Test equality and comparison."""

    def test_two_postal_codes_with_same_value_are_equal(self):
        """Test that postal codes with same value are equal."""
        postal_code1 = PostalCode("10115")
        postal_code2 = PostalCode("10115")

        assert postal_code1 == postal_code2

    def test_two_postal_codes_with_different_values_are_not_equal(self):
        """Test that postal codes with different values are not equal."""
        postal_code1 = PostalCode("10115")
        postal_code2 = PostalCode("12045")

        assert postal_code1 != postal_code2

    def test_postal_code_equality_after_whitespace_stripping(self):
        """Test that postal codes are equal after whitespace stripping."""
        postal_code1 = PostalCode("10115")
        postal_code2 = PostalCode("  10115  ")

        assert postal_code1 == postal_code2


class TestPostalCodeRepr:
    """Test string representation."""

    def test_repr_contains_postal_code_value(self):
        """Test that repr contains postal code value."""
        postal_code = PostalCode("10115")

        repr_str = repr(postal_code)
        assert "PostalCode" in repr_str
        assert "10115" in repr_str

    def test_str_representation(self):
        """Test string representation."""
        postal_code = PostalCode("10115")

        str_repr = str(postal_code)
        assert str_repr is not None
        assert len(str_repr) > 0


class TestPostalCodeEdgeCases:
    """Test edge cases and boundary values."""

    def test_all_valid_prefix_ranges(self):
        """Test that all valid Berlin postal code prefixes work."""
        valid_prefixes = ["10", "12", "13", "14"]

        for prefix in valid_prefixes:
            postal_code = PostalCode(f"{prefix}115")
            assert postal_code.value == f"{prefix}115"

    def test_postal_code_with_leading_zeros_in_valid_range(self):
        """Test postal code with pattern 10xxx."""
        postal_codes = ["10001", "10115", "10999"]

        for code in postal_codes:
            postal_code = PostalCode(code)
            assert postal_code.value == code

    def test_postal_code_range_12xxx(self):
        """Test various postal codes in 12xxx range."""
        postal_codes = ["12001", "12045", "12999"]

        for code in postal_codes:
            postal_code = PostalCode(code)
            assert postal_code.value == code

    def test_postal_code_range_13xxx(self):
        """Test various postal codes in 13xxx range."""
        postal_codes = ["13001", "13353", "13999"]

        for code in postal_codes:
            postal_code = PostalCode(code)
            assert postal_code.value == code

    def test_postal_code_range_14xxx(self):
        """Test various postal codes in 14xxx range."""
        postal_codes = ["14001", "14100", "14199"]

        for code in postal_codes:
            postal_code = PostalCode(code)
            assert postal_code.value == code

    def test_postal_code_boundary_conditions(self):
        """Test PostalCode validation at boundaries through public interface."""
        # Valid: 10001 to 14199 - should create successfully
        postal_code_1 = PostalCode("10001")
        assert postal_code_1.value == "10001"

        postal_code_2 = PostalCode("14199")
        assert postal_code_2.value == "14199"

        # Invalid: at boundaries - should raise exceptions
        with pytest.raises(InvalidPostalCodeError):
            PostalCode("10000")

        with pytest.raises(InvalidPostalCodeError):
            PostalCode("14200")


class TestPostalCodeIntegration:
    """Integration tests for PostalCode value object."""

    def test_postal_code_complete_workflow(self):
        """Test complete workflow with PostalCode."""
        # Create postal code with whitespace
        postal_code = PostalCode("  10115  ")

        # Verify it was cleaned and stored correctly
        assert postal_code.value == "10115"

        # Verify immutability
        with pytest.raises(AttributeError):
            postal_code.value = "12045"

        # Use in get_values
        values = PostalCode.get_values([postal_code])
        assert values == ["10115"]

    def test_multiple_postal_codes_in_collection(self):
        """Test creating and using multiple postal codes."""
        postal_codes = [PostalCode("10115"), PostalCode("12045"), PostalCode("13353"), PostalCode("14199")]

        assert len(postal_codes) == 4
        assert all(isinstance(pc, PostalCode) for pc in postal_codes)

        values = PostalCode.get_values(postal_codes)
        assert len(values) == 4
        assert values == ["10115", "12045", "13353", "14199"]

    def test_postal_codes_in_dictionary(self):
        """Test storing postal codes in dictionary."""
        postal_dict = {"area1": PostalCode("10115"), "area2": PostalCode("12045"), "area3": PostalCode("13353")}

        assert len(postal_dict) == 3
        assert postal_dict["area1"].value == "10115"
        assert postal_dict["area2"].value == "12045"

    def test_postal_code_in_set(self):
        """Test using postal codes in a set."""
        postal_set = {PostalCode("10115"), PostalCode("12045"), PostalCode("10115")}  # Duplicate

        # Set should contain only 2 unique postal codes
        assert len(postal_set) == 2

    def test_postal_code_consistency(self):
        """Test that postal code value remains consistent."""
        postal_code = PostalCode("10115")

        # Access value multiple times
        value1 = postal_code.value
        value2 = postal_code.value
        value3 = postal_code.value

        assert value1 == value2 == value3 == "10115"

    def test_get_values_with_various_postal_codes(self):
        """Test get_values with comprehensive list."""
        postal_codes = [
            PostalCode("10001"),
            PostalCode("10999"),
            PostalCode("12001"),
            PostalCode("12999"),
            PostalCode("13001"),
            PostalCode("13999"),
            PostalCode("14001"),
            PostalCode("14199"),
        ]

        values = PostalCode.get_values(postal_codes)

        assert len(values) == 8
        assert values[0] == "10001"
        assert values[-1] == "14199"


class TestPostalCodeErrorMessages:
    """Test error message content and clarity."""

    def test_numeric_error_message_includes_value(self):
        """Test that numeric error message includes the invalid value."""
        with pytest.raises(InvalidPostalCodeError) as exc_info:
            PostalCode("ABC12")

        assert "ABC12" in str(exc_info.value)
        assert "numeric" in str(exc_info.value)

    def test_length_error_message_includes_value(self):
        """Test that length error message includes the invalid value."""
        with pytest.raises(InvalidPostalCodeError) as exc_info:
            PostalCode("123")

        assert "123" in str(exc_info.value)
        assert "5 digits" in str(exc_info.value)

    def test_berlin_rule_error_message_includes_value(self):
        """Test that Berlin rule error message includes the invalid value."""
        with pytest.raises(InvalidPostalCodeError) as exc_info:
            PostalCode("99999")

        assert "99999" in str(exc_info.value)
        assert "10, 12, 13, or 14" in str(exc_info.value)
