"""
CSV-based implementation of PopulationRepository.
"""

from typing import List

from src.shared.domain.value_objects import PostalCode
from src.shared.infrastructure.repositories import CSVRepository, PopulationRepository


class CSVPopulationRepository(PopulationRepository, CSVRepository):
    """
    CSV-based implementation of `PopulationRepository`.

    This repository provides residents / population data for postal codes.
    """

    def __init__(self, file_path: str):
        """
        Initialize `CSVPopulationRepository` with CSV file path.

        Args:
            file_path (str): Path to the population CSV file.
        """
        super().__init__(file_path)

        self._df = self._load_csv(sep=",")
        self._transform()

    def _transform(self):
        """
        Transform the loaded DataFrame for consistent data types.
        """

        # Ensure string type for comparison and replace ',' with '.' for decimal consistency.
        self._df["plz"] = self._df["plz"].astype(str)
        self._df["lat"] = self._df["lat"].astype(str).str.replace(",", ".")
        self._df["lon"] = self._df["lon"].astype(str).str.replace(",", ".")

    def get_all_postal_codes(self) -> List[PostalCode]:
        """
        Get all postal codes with population data.

        Returns:
            List of PostalCode value objects
        """
        postal_codes: List[PostalCode] = []
        for plz in self._df["plz"].unique():
            try:
                postal_code = PostalCode(plz)
                postal_codes.append(postal_code)
            except ValueError:
                # Skip invalid postal codes.
                continue

        return postal_codes

    def get_residents_count(self, postal_code: PostalCode) -> int:
        """
        Get the number of residents for a given postal code.

        Args:
            postal_code (PostalCode): Postal code to get resident count for.
        Returns:
            int: Number of residents in the given postal code.
        """
        df_filtered = self._df[self._df["plz"] == postal_code.value]

        if df_filtered.empty:
            return 0

        residents_count = df_filtered["einwohner"].sum()

        return int(residents_count)
