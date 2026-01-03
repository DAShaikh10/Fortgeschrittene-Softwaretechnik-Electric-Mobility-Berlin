"""
Unit Tests for PopulationRepository.

Test categories:
- Abstract base class tests
- Abstract method tests
- Concrete implementation tests
"""

# pylint: disable=redefined-outer-name

from typing import List
from unittest.mock import MagicMock

import pytest

from src.shared.domain.exceptions import InvalidPostalCodeError
from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.repositories.PopulationRepository import PopulationRepository


# Create a concrete implementation for testing
class ConcretePopulationRepository(PopulationRepository):
    """Concrete implementation of PopulationRepository for testing purposes."""

    def __init__(self, postal_codes: List[PostalCode]):
        """Initialize the concrete repository with a list of postal codes."""
        self._postal_codes = postal_codes

    def get_all_postal_codes(self) -> List[PostalCode]:
        """Get all postal codes."""
        return self._postal_codes.copy()


# Test fixtures
@pytest.fixture
def postal_code_list():
    """Create a list of postal codes for testing."""
    return [
        PostalCode("10115"),
        PostalCode("10117"),
        PostalCode("10119"),
        PostalCode("10178"),
        PostalCode("10179")
    ]


@pytest.fixture
def empty_postal_code_list():
    """Create an empty list of postal codes for testing."""
    return []


@pytest.fixture
def single_postal_code():
    """Create a single postal code for testing."""
    return PostalCode("10115")


class TestPopulationRepositoryAbstractBaseClass:
    """Test that PopulationRepository is an abstract base class."""

    def test_is_abstract_base_class(self):
        """Test that PopulationRepository is an abstract base class."""
        from abc import ABC

        assert issubclass(PopulationRepository, ABC)

    def test_cannot_instantiate_abstract_class_directly(self):
        """Test that PopulationRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PopulationRepository()  # Should fail as it has abstract methods

    def test_has_abstract_method_get_all_postal_codes(self):
        """Test that PopulationRepository has abstract method get_all_postal_codes."""
        from abc import ABC

        # Check that get_all_postal_codes is abstract
        assert hasattr(PopulationRepository, 'get_all_postal_codes')
        # Check if it's an abstract method
        assert hasattr(PopulationRepository.get_all_postal_codes, '__isabstractmethod__')
        assert PopulationRepository.get_all_postal_codes.__isabstractmethod__ is True


class TestPopulationRepositoryConcreteImplementation:
    """Test concrete implementation of PopulationRepository."""

    def test_concrete_implementation_can_be_instantiated(self, postal_code_list):
        """Test that a concrete implementation can be instantiated."""
        repo = ConcretePopulationRepository(postal_code_list)

        assert isinstance(repo, PopulationRepository)
        assert repo._postal_codes == postal_code_list

    def test_concrete_implementation_implements_get_all_postal_codes(
        self, postal_code_list
    ):
        """Test that concrete implementation implements get_all_postal_codes."""
        repo = ConcretePopulationRepository(postal_code_list)

        result = repo.get_all_postal_codes()

        assert isinstance(result, list)
        assert len(result) == len(postal_code_list)
        assert all(isinstance(plz, PostalCode) for plz in result)

    def test_get_all_postal_codes_returns_list_of_postal_codes(
        self, postal_code_list
    ):
        """Test that get_all_postal_codes returns list of PostalCode objects."""
        repo = ConcretePopulationRepository(postal_code_list)

        result = repo.get_all_postal_codes()

        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(plz, PostalCode) for plz in result)
        assert result == postal_code_list

    def test_get_all_postal_codes_returns_empty_list_when_no_data(
        self, empty_postal_code_list
    ):
        """Test that get_all_postal_codes returns empty list when no data."""
        repo = ConcretePopulationRepository(empty_postal_code_list)

        result = repo.get_all_postal_codes()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_all_postal_codes_returns_copy_not_reference(
        self, postal_code_list
    ):
        """Test that get_all_postal_codes returns a copy, not a reference."""
        repo = ConcretePopulationRepository(postal_code_list)

        result1 = repo.get_all_postal_codes()
        result2 = repo.get_all_postal_codes()

        # Results should be equal but not the same object
        assert result1 == result2
        assert result1 is not result2

    def test_get_all_postal_codes_handles_single_postal_code(
        self, single_postal_code
    ):
        """Test that get_all_postal_codes handles single postal code."""
        repo = ConcretePopulationRepository([single_postal_code])

        result = repo.get_all_postal_codes()

        assert len(result) == 1
        assert result[0] == single_postal_code

    def test_get_all_postal_codes_preserves_order(self):
        """Test that get_all_postal_codes preserves order of postal codes."""
        postal_codes = [
            PostalCode("10179"),
            PostalCode("10115"),
            PostalCode("10119"),
            PostalCode("10117"),
            PostalCode("10178")
        ]
        repo = ConcretePopulationRepository(postal_codes)

        result = repo.get_all_postal_codes()

        assert result == postal_codes
        assert result[0].value == "10179"
        assert result[1].value == "10115"
        assert result[4].value == "10178"


class TestPopulationRepositoryInterface:
    """Test the PopulationRepository interface contract."""

    def test_interface_defines_get_all_postal_codes(self):
        """Test that the interface defines get_all_postal_codes method."""
        assert hasattr(PopulationRepository, 'get_all_postal_codes')
        assert callable(PopulationRepository.get_all_postal_codes)

    def test_get_all_postal_codes_signature(self):
        """Test that get_all_postal_codes has correct signature."""
        import inspect

        sig = inspect.signature(PopulationRepository.get_all_postal_codes)
        
        # Should have only self as parameter
        assert len(sig.parameters) == 1
        assert 'self' in sig.parameters
        
        # Return type annotation should be List[PostalCode]
        return_annotation = sig.return_annotation
        assert return_annotation is not inspect.Signature.empty

    def test_concrete_implementation_must_implement_get_all_postal_codes(self):
        """Test that concrete implementations must implement get_all_postal_codes."""
        # Create an incomplete implementation
        class IncompleteRepository(PopulationRepository):
            pass

        # Should raise TypeError when trying to instantiate
        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_concrete_implementation_can_be_used_polymorphically(
        self, postal_code_list
    ):
        """Test that concrete implementations can be used polymorphically."""
        repo = ConcretePopulationRepository(postal_code_list)

        # Should be usable as PopulationRepository
        def process_repository(repository: PopulationRepository) -> List[PostalCode]:
            return repository.get_all_postal_codes()

        result = process_repository(repo)

        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(plz, PostalCode) for plz in result)


class TestPopulationRepositoryIntegration:
    """Integration tests for PopulationRepository."""

    def test_multiple_repositories_with_different_data(self):
        """Test that multiple repositories can work with different data."""
        postal_codes_1 = [PostalCode("10115"), PostalCode("10117")]
        postal_codes_2 = [PostalCode("10119"), PostalCode("10178"), PostalCode("10179")]

        repo1 = ConcretePopulationRepository(postal_codes_1)
        repo2 = ConcretePopulationRepository(postal_codes_2)

        result1 = repo1.get_all_postal_codes()
        result2 = repo2.get_all_postal_codes()

        assert len(result1) == 2
        assert len(result2) == 3
        assert result1 != result2

    def test_repository_handles_duplicate_postal_codes(self):
        """Test that repository can handle duplicate postal codes if needed."""
        postal_codes = [
            PostalCode("10115"),
            PostalCode("10115"),  # Duplicate
            PostalCode("10117")
        ]
        repo = ConcretePopulationRepository(postal_codes)

        result = repo.get_all_postal_codes()

        # Should return all postal codes including duplicates
        assert len(result) == 3
        assert result[0] == result[1]

    def test_repository_works_with_empty_implementation(self, empty_postal_code_list):
        """Test that repository works correctly with empty data."""
        repo = ConcretePopulationRepository(empty_postal_code_list)

        result = repo.get_all_postal_codes()

        assert isinstance(result, list)
        assert len(result) == 0

    def test_repository_interface_contract(self, postal_code_list):
        """Test that repository follows the interface contract."""
        repo = ConcretePopulationRepository(postal_code_list)

        # Verify it's an instance of the abstract class
        assert isinstance(repo, PopulationRepository)

        # Verify it implements the required method
        assert hasattr(repo, 'get_all_postal_codes')
        assert callable(repo.get_all_postal_codes)

        # Verify the method returns the correct type
        result = repo.get_all_postal_codes()
        assert isinstance(result, list)
        assert all(isinstance(plz, PostalCode) for plz in result)


class TestPostalCodeBoundedContextRules:
    """Test postal code bounded context rules in repository context.
    
    Bounded Context Rules:
    - Postal Code Format: Numeric and exactly 5 digits
    - Region Support: Must start with 10, 12, 13, or 14
    """

    def test_valid_postal_codes_starting_with_10(self):
        """Test that postal codes starting with 10 are valid."""
        valid_codes = [
            "10001",  # Minimum boundary (must be > 10000)
            "10115",
            "10117",
            "10999",  # Maximum for 10 prefix
        ]
        
        for code in valid_codes:
            postal_code = PostalCode(code)
            repo = ConcretePopulationRepository([postal_code])
            result = repo.get_all_postal_codes()
            assert len(result) == 1
            assert result[0].value == code

    def test_valid_postal_codes_starting_with_12(self):
        """Test that postal codes starting with 12 are valid."""
        valid_codes = [
            "12000",  # Minimum boundary
            "12115",
            "12117",
            "12999",  # Maximum for 12 prefix
        ]
        
        for code in valid_codes:
            postal_code = PostalCode(code)
            repo = ConcretePopulationRepository([postal_code])
            result = repo.get_all_postal_codes()
            assert len(result) == 1
            assert result[0].value == code

    def test_valid_postal_codes_starting_with_13(self):
        """Test that postal codes starting with 13 are valid."""
        valid_codes = [
            "13000",  # Minimum boundary
            "13115",
            "13117",
            "13999",  # Maximum for 13 prefix
        ]
        
        for code in valid_codes:
            postal_code = PostalCode(code)
            repo = ConcretePopulationRepository([postal_code])
            result = repo.get_all_postal_codes()
            assert len(result) == 1
            assert result[0].value == code

    def test_valid_postal_codes_starting_with_14(self):
        """Test that postal codes starting with 14 are valid."""
        valid_codes = [
            "14000",  # Minimum boundary
            "14115",
            "14117",
            "14199",  # Maximum for 14 prefix (must be < 14200)
        ]
        
        for code in valid_codes:
            postal_code = PostalCode(code)
            repo = ConcretePopulationRepository([postal_code])
            result = repo.get_all_postal_codes()
            assert len(result) == 1
            assert result[0].value == code

    def test_invalid_postal_code_non_numeric(self):
        """Test that non-numeric postal codes are rejected."""
        invalid_codes = [
            "1011a",  # Contains letter
            "10-15",  # Contains hyphen
            "10 15",  # Contains space
            "abcde",  # All letters
            "10.15",  # Contains dot
        ]
        
        for code in invalid_codes:
            with pytest.raises(InvalidPostalCodeError, match="must be numeric"):
                PostalCode(code)

    def test_invalid_postal_code_wrong_length(self):
        """Test that postal codes with wrong length are rejected."""
        invalid_codes = [
            "1011",   # 4 digits (too short)
            "10115",  # 5 digits (valid, but test other lengths)
            "101155", # 6 digits (too long)
            "10",     # 2 digits (too short)
            "1011555", # 7 digits (too long)
        ]
        
        for code in invalid_codes:
            if len(code) != 5:
                with pytest.raises(InvalidPostalCodeError, match="exactly 5 digits"):
                    PostalCode(code)

    def test_invalid_postal_code_wrong_starting_digits(self):
        """Test that postal codes not starting with 10, 12, 13, or 14 are rejected."""
        invalid_codes = [
            "09000",  # Starts with 09
            "11000",  # Starts with 11
            "15000",  # Starts with 15
            "20000",  # Starts with 20
            "99999",  # Starts with 99
        ]
        
        for code in invalid_codes:
            with pytest.raises(InvalidPostalCodeError, match="must start with 10, 12, 13, or 14"):
                PostalCode(code)

    def test_invalid_postal_code_boundary_conditions(self):
        """Test boundary conditions for postal code validation."""
        # Test codes just outside valid range
        invalid_codes = [
            "10000",  # At lower boundary (must be > 10000)
            "09999",  # Just below 10000
            "14200",  # At upper boundary (must be < 14200)
            "14201",  # Just above boundary
            "15000",  # Well above boundary
        ]
        
        for code in invalid_codes:
            with pytest.raises(InvalidPostalCodeError):
                PostalCode(code)

    def test_invalid_postal_code_empty_or_none(self):
        """Test that empty or None postal codes are rejected."""
        with pytest.raises(InvalidPostalCodeError, match="cannot be None or empty"):
            PostalCode("")
        
        with pytest.raises(InvalidPostalCodeError, match="cannot be None or empty"):
            PostalCode("   ")  # Whitespace only

    def test_valid_postal_codes_all_regions_in_repository(self):
        """Test that repository can handle postal codes from all valid regions."""
        postal_codes = [
            PostalCode("10115"),  # Region 10
            PostalCode("12115"),  # Region 12
            PostalCode("13115"),  # Region 13
            PostalCode("14115"),  # Region 14
        ]
        
        repo = ConcretePopulationRepository(postal_codes)
        result = repo.get_all_postal_codes()
        
        assert len(result) == 4
        assert all(isinstance(plz, PostalCode) for plz in result)
        assert result[0].value == "10115"
        assert result[1].value == "12115"
        assert result[2].value == "13115"
        assert result[3].value == "14115"

    def test_repository_rejects_invalid_postal_codes_during_creation(self):
        """Test that repository cannot be created with invalid postal codes."""
        # This test verifies that invalid postal codes are caught at PostalCode creation
        # before they can be added to the repository
        
        # Try to create invalid postal codes - should fail before repository creation
        with pytest.raises(InvalidPostalCodeError):
            PostalCode("99999")  # Invalid starting digits
        
        with pytest.raises(InvalidPostalCodeError):
            PostalCode("1011")  # Wrong length
        
        with pytest.raises(InvalidPostalCodeError):
            PostalCode("1011a")  # Non-numeric

    def test_postal_code_format_enforced_numeric_only(self):
        """Test that postal code format enforces numeric-only requirement."""
        # Valid numeric codes
        valid_numeric = ["10115", "12115", "13115", "14115"]
        for code in valid_numeric:
            postal_code = PostalCode(code)
            assert postal_code.value == code
        
        # Invalid non-numeric codes
        invalid_non_numeric = ["1011a", "10-15", "10.15", "10 15"]
        for code in invalid_non_numeric:
            with pytest.raises(InvalidPostalCodeError, match="must be numeric"):
                PostalCode(code)

    def test_postal_code_format_enforced_exactly_five_digits(self):
        """Test that postal code format enforces exactly 5 digits requirement."""
        # Valid 5-digit codes
        valid_length = ["10115", "12115", "13115", "14115"]
        for code in valid_length:
            postal_code = PostalCode(code)
            assert len(postal_code.value) == 5
        
        # Invalid lengths
        invalid_lengths = {
            "1011": "exactly 5 digits",    # 4 digits
            "101155": "exactly 5 digits",  # 6 digits
            "10": "exactly 5 digits",     # 2 digits
        }
        
        for code, expected_error in invalid_lengths.items():
            with pytest.raises(InvalidPostalCodeError, match=expected_error):
                PostalCode(code)

    def test_region_support_all_valid_prefixes(self):
        """Test that all valid region prefixes (10, 12, 13, 14) are supported."""
        valid_prefixes = {
            "10": ["10001", "10115", "10999"],  # Must be > 10000
            "12": ["12000", "12115", "12999"],
            "13": ["13000", "13115", "13999"],
            "14": ["14000", "14115", "14199"],  # Must be < 14200
        }
        
        for prefix, codes in valid_prefixes.items():
            for code in codes:
                postal_code = PostalCode(code)
                assert postal_code.value.startswith(prefix)
                repo = ConcretePopulationRepository([postal_code])
                result = repo.get_all_postal_codes()
                assert len(result) == 1
                assert result[0].value == code

    def test_region_support_invalid_prefixes_rejected(self):
        """Test that invalid region prefixes are rejected."""
        invalid_prefixes = ["09", "11", "15", "20", "99"]
        
        for prefix in invalid_prefixes:
            # Create a 5-digit code with invalid prefix
            invalid_code = prefix + "000"
            with pytest.raises(InvalidPostalCodeError, match="must start with 10, 12, 13, or 14"):
                PostalCode(invalid_code)

    def test_postal_code_validation_in_repository_context(self):
        """Test that postal code validation works correctly in repository context."""
        # Valid postal codes should work in repository
        valid_codes = [
            PostalCode("10115"),
            PostalCode("12115"),
            PostalCode("13115"),
            PostalCode("14115"),
        ]
        
        repo = ConcretePopulationRepository(valid_codes)
        result = repo.get_all_postal_codes()
        
        assert len(result) == 4
        assert all(isinstance(plz, PostalCode) for plz in result)
        
        # Verify all returned codes are valid
        for postal_code in result:
            assert len(postal_code.value) == 5
            assert postal_code.value.isdigit()
            assert postal_code.value.startswith(("10", "12", "13", "14"))