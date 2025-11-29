import os

# Setup - Determine the current working directory so that the rest of the code can use relative paths correctly.
cwd = os.getcwd()
print("DEBUG: Current working directory:\n" + cwd)

# Imports.
from config import pdict  # Serves as the project configuration dictionary.

from core import methods as mt
from core import helper_tools as ht


@ht.timer
def main() -> None:
    """
    Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin with power categories and search functionality.
    """

    # Load datasets.
    # df_geodat_plz: Geodata Berlin PLZ - Postal codes for Berlin with geocoordinates.
    # df_lstat: Ladesäulenregister - Electric charging stations in Germany.
    # df_residents: PLZ Einwohner - Residents per postal code in Germany.
    df_geodat_plz, df_lstat, df_residents = mt.load_datasets(pdict)

    # Preprocess the charging stations data.
    df_lstat2 = mt.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    gdf_lstat3 = mt.count_plz_occurrences(df_lstat2)
    gdf_lstat3_kW = mt.count_plz_occurrences_by_kw(df_lstat2)

    # Preprocess the residents data.
    gdf_residents2 = mt.preprop_resid(df_residents, df_geodat_plz, pdict)

    # ========== DATA QUALITY ANALYSIS ==========
    # Perform comprehensive data quality checks and outlier detection
    # This generates visualizations and statistical summaries to identify anomalies
    mt.analyze_data_quality_and_outliers(
        df_geodat_plz=df_geodat_plz,
        df_lstat=df_lstat,
        df_residents=df_residents,
        gdf_lstat3=gdf_lstat3,
        gdf_residents2=gdf_residents2
    )
    # ========== END DATA QUALITY ANALYSIS ==========

    # Calculate demand priority analysis.
    demand_analysis = mt.calculate_demand_priority(gdf_residents2, gdf_lstat3)

    # Print demand analysis summary.
    # NOTE: This helps answer the sub-task #7 in the Task layed out in LMS.
    mt.demand_analysis_summary(demand_analysis)

    # Generate the Streamlit App for visualizing electric charging stations & residents in Berlin.
    mt.make_streamlit_electric_charging_resid(gdf_lstat3, gdf_residents2, gdf_lstat3_kW, demand_analysis)


if __name__ == "__main__":
    main()
