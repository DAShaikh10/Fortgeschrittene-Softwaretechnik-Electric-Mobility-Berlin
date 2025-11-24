import os

# Setup - Determine the current working directory so that the rest of the code can use relative paths correctly.
cwd = os.getcwd()
print("DEBUG: Current working directory:\n" + cwd)

# Imports.
from config import pdict

import pandas as pd
from core import methods as mt
from core import helper_tools as ht


def load_datasets() -> tuple[pd.DataFrame]:
    """
    Loads the required datasets for the application.

    Returns:
        tuple[pd.DataFrame]: A tuple containing the loaded dataframes in the order:
                             (geodata_berlin_plz, Ladesaeulenregister, plz_einwohner)
    """

    # Determine the 'geodata_berlin_plz' dataset path.
    geodat_plz_file_path = os.path.join(cwd, pdict["dataset_folder"], pdict["file_geodat_plz"])

    # Determine the 'Ladesaeulenregister' dataset path.
    lstat_file_path = os.path.join(cwd, pdict["dataset_folder"], pdict["file_lstations"])

    # Determine the 'plz_einwohner' dataset path.
    resid_file_path = os.path.join(cwd, pdict["dataset_folder"], pdict["file_residents"])

    # Load datasets.
    df_geodat_plz = pd.read_csv(geodat_plz_file_path, delimiter=";")
    df_lstat = pd.read_csv(lstat_file_path, encoding="Windows-1252", sep=";", low_memory=False, skiprows=10)
    df_residents = pd.read_csv(resid_file_path, sep=",")

    return (df_geodat_plz, df_lstat, df_residents)


def filter_federal_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the `geodata_berlin_plz` dataset for Berlin only.
    """

    filtered_df = df[df["Bundesland"] == "Berlin"].copy()

    return filtered_df


@ht.timer
def main() -> None:
    """
    Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin with power categories and search functionality.
    """

    # Load datasets.
    # df_geodat_plz: Geodata Berlin PLZ - Postal codes for Berlin with geocoordinates.
    # df_lstat: Ladesäulenregister - Electric charging stations in Germany.
    # df_residents: PLZ Einwohner - Residents per postal code in Germany.
    df_geodat_plz, df_lstat, df_residents = load_datasets()

    # Filter the data for Berlin Federal State (Bundesland) only.
    df_lstat = filter_federal_state(df_lstat)

    # Preprocess the charging stations data.
    df_lstat2 = mt.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    
    # Count charging stations by power category
    power_category_dict = mt.count_plz_by_power_category(df_lstat2)

    # Preprocess the residents data.
    gdf_residents2 = mt.preprop_resid(df_residents, df_geodat_plz, pdict)

    # Generate the Streamlit App with power categories and search functionality
    mt.make_streamlit_with_enhanced_features(power_category_dict, gdf_residents2, df_lstat2)


if __name__ == "__main__":
    main()
