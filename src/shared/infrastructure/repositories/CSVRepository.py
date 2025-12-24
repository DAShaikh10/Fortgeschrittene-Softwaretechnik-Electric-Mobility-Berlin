"""
Base CSV Repository Module.
"""

import pandas as pd


class CSVRepository:
    """
    Base class for CSV-based repositories.
    Provides common functionality for loading CSV files.
    """

    def __init__(self, file_path: str):
        """
        Initialize `CSVRepository` with CSV file path.
        """
        self._file_path = file_path

    def _load_csv(self, sep: str, **kwargs) -> pd.DataFrame:
        """
        Load a CSV file and return its contents as a pandas DataFrame.

        Args:
            sep (str): The separator used in the CSV file.
            **kwargs: Additional keyword arguments passed to `pandas.read_csv`

        Returns:
            pd.DataFrame: The contents of the CSV file.
        """

        return pd.read_csv(self._file_path, sep=sep, **kwargs)
