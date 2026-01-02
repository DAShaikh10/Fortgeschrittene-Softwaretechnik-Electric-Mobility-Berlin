"""
Demand Analysis In-Memory Repository Module.
"""

from typing import Dict, List, Optional

from src.shared.domain.value_objects import PostalCode
from src.demand.domain.aggregates import DemandAnalysisAggregate

from .DemandAnalysisRepository import DemandAnalysisRepository


class InMemoryDemandAnalysisRepository(DemandAnalysisRepository):
    """
    In Memory implementation of DemandAnalysisRepository.
    Stores demand analysis data in memory for quick access during runtime.

    Use case: Testing, prototyping, or single-session applications.
    """

    def __init__(self):
        """
        Initialize repository with empty storage.
        """
        self._storage: Dict[str, DemandAnalysisAggregate] = {}

    def save(self, aggregate: DemandAnalysisAggregate) -> None:
        """
        Save or update a demand analysis aggregate.

        Args:
            aggregate: DemandAnalysisAggregate to save
        """
        if not isinstance(aggregate, DemandAnalysisAggregate):
            raise TypeError("Must be a DemandAnalysisAggregate")

        key = aggregate.postal_code.value
        self._storage[key] = aggregate

    def find_by_postal_code(self, postal_code: PostalCode) -> Optional[DemandAnalysisAggregate]:
        """
        Find demand analysis by postal code.

        Args:
            postal_code: PostalCode to search for

        Returns:
            Optional[DemandAnalysisAggregate]: Found aggregate or None
        """
        if not isinstance(postal_code, PostalCode):
            raise TypeError("postal_code must be a PostalCode value object")

        return self._storage.get(postal_code.value)

    def find_all(self) -> List[DemandAnalysisAggregate]:
        """
        Find all demand analyses.

        Returns:
            List[DemandAnalysisAggregate]: All saved aggregates
        """
        return list(self._storage.values())

    def delete(self, postal_code: PostalCode) -> bool:
        """
        Delete demand analysis by postal code.

        Args:
            postal_code: PostalCode to delete

        Returns:
            bool: True if deleted, False if not found
        """
        if not isinstance(postal_code, PostalCode):
            raise TypeError("postal_code must be a PostalCode value object")

        key = postal_code.value
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def exists(self, postal_code: PostalCode) -> bool:
        """
        Check if demand analysis exists for postal code.

        Args:
            postal_code: PostalCode to check

        Returns:
            bool: True if exists, False otherwise
        """
        if not isinstance(postal_code, PostalCode):
            raise TypeError("postal_code must be a PostalCode value object")

        return postal_code.value in self._storage

    def count(self) -> int:
        """
        Count total number of demand analyses.

        Returns:
            int: Total count
        """
        return len(self._storage)

    def clear(self) -> None:
        """
        Clear all stored analyses. Useful for testing.
        """
        self._storage.clear()

    def find_by_priority_level(self, priority_level: str) -> List[DemandAnalysisAggregate]:
        """
        Find all analyses with specific priority level.

        Args:
            priority_level: Priority level to filter by ("High", "Medium", "Low")

        Returns:
            List[DemandAnalysisAggregate]: Matching aggregates
        """
        return [agg for agg in self._storage.values() if agg.demand_priority.level.value == priority_level]
