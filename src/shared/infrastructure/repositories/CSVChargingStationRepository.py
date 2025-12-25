"""
Shared Infratructure - CSV Charging Station Repository Implementation
"""

from typing import List

from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import PostalCode

from .CSVRepository import CSVRepository
from .ChargingStationRepository import ChargingStationRepository


class CSVChargingStationRepository(ChargingStationRepository, CSVRepository):
    """
    CSV-based implementation of `ChargingStationRepository`.

    This repository provides charging station data for postal codes.
    """

    def __init__(self, file_path: str):
        """
        Initialize `CSVChargingStationRepository` with CSV file path.

        Args:
            file_path (str): Path to the charging station CSV file.
        """
        super().__init__(file_path)

        self._df = self._load_csv(sep=";", encoding="Windows-1252", low_memory=False, skiprows=10)
        self._transform()

    def _transform(self):
        """
        Transform the loaded DataFrame for consistent data types.
        """

        self._df = self._df.loc[
            :,
            [
                "Postleitzahl",
                "Bundesland",
                "Breitengrad",
                "Längengrad",
                "Nennleistung Ladeeinrichtung [kW]",
            ],
        ]
        self._df.rename(
            columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"},
            inplace=True,  # In-place and hence no reassignment needed.
        )

        # Normalize data types and decimal separators for consistent processing.
        # German CSV format uses comma as decimal separator; convert to period for Python float parsing.
        self._df["PLZ"] = self._df["PLZ"].astype(str)
        self._df["Breitengrad"] = self._df["Breitengrad"].astype(str).str.replace(",", ".")
        self._df["Längengrad"] = self._df["Längengrad"].astype(str).str.replace(",", ".")
        self._df["KW"] = self._df["KW"].astype(str).str.replace(",", ".")

    def find_stations_by_postal_code(self, postal_code: PostalCode) -> List[ChargingStation]:
        """
        Find charging stations by postal code.

        Args:
            postal_code (PostalCode): Postal code to search for.
        Returns:
            List of ChargingStation entities found.
        """

        charging_stations = self._df[self._df["PLZ"] == postal_code.value]
        stations: List[ChargingStation] = []
        for _, row in charging_stations.iterrows():
            station = ChargingStation(
                postal_code=postal_code,
                latitude=float(row["Breitengrad"]),
                longitude=float(row["Längengrad"]),
                power_kw=float(row["KW"]),
            )
            stations.append(station)

        return stations
