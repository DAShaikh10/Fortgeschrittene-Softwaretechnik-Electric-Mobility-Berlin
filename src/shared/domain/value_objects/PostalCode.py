"""
Shared Domain Value Object - Postal Code
"""

from dataclasses import dataclass

from src.shared.domain.exceptions import InvalidPostalCodeError


@dataclass(frozen=True)
class PostalCode:
    """
    Berlin Postal Code Value Object.

    Business Rules:
    - Must be exactly 5 digits.
    - Must be numeric.
    - Must start with 10, 12, 13, or 14 (Berlin specific).

    Invariants enforced in constructor to maintain validity.
    """

    value: str

    @staticmethod
    def _is_berlin_postal_code(plz: str) -> bool:
        return 10000 < int(plz) < 14200

    def __post_init__(self):
        """
        Validate postal code on creation (invariant enforcement).
        """

        if self.value is None or (isinstance(self.value, str) and not self.value.strip()):
            raise InvalidPostalCodeError("Postal code cannot be None or empty.")

        # Clean the value.
        cleaned = str(self.value).strip()
        object.__setattr__(self, "value", cleaned)

        # Validation rules.
        if not cleaned.isdigit():
            raise InvalidPostalCodeError(f"Postal code must be numeric: '{cleaned}'.")

        if len(cleaned) != 5:
            raise InvalidPostalCodeError(f"Postal code must be exactly 5 digits: '{cleaned}'.")

        # Berlin-specific rule.
        if not cleaned.startswith(("10", "12", "13", "14")) or not self._is_berlin_postal_code(cleaned):
            raise InvalidPostalCodeError(f"Berlin postal code must start with 10, 12, 13, or 14: '{cleaned}'.")

    @staticmethod
    def get_values(postal_codes: list["PostalCode"]) -> list[str]:
        """
        Extract string values from a list of PostalCode value objects.

        Args:
            postal_codes (list[PostalCode]): List of PostalCode value objects.

        Returns:
            list of string postal code values."""
        return [plz.value for plz in postal_codes]
