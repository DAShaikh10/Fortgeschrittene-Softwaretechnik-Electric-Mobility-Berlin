"""
Shared Domain Enum - Coverage Assessment
"""

from enum import Enum


class CoverageAssessment(Enum):
    """
    Enumeration for demand-based coverage assessment levels.

    Used by DemandAnalysisAggregate to assess infrastructure adequacy
    based on population-to-station ratios.
    """

    CRITICAL = "CRITICAL"
    POOR = "POOR"
    ADEQUATE = "ADEQUATE"
    GOOD = "GOOD"
