"""
Shared Domain Enum - Coverage Level
"""

from enum import Enum


class CoverageLevel(Enum):
    """
    Enumeration for infrastructure coverage levels.

    Used by PostalCodeAreaAggregate to assess charging station coverage.
    """

    NO_COVERAGE = "NO_COVERAGE"
    POOR = "POOR"
    ADEQUATE = "ADEQUATE"
    GOOD = "GOOD"
    EXCELLENT = "EXCELLENT"
