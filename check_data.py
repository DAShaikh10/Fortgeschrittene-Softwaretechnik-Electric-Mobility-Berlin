import pandas as pd

from config import pdict
from core import methods as mt


def check_required_columns(df, required_cols, dataset_name):
    """
    Checks if specific columns exist in the DataFrame.
    Returns: (bool, dict) -> (Passed?, Report Row)
    """

    missing = [c for c in required_cols if c not in df.columns]
    status = "FAIL" if missing else "PASS"
    details = f"Missing columns: {missing}" if missing else "All required columns present"

    report_row = {"Dataset": dataset_name, "Check": "Required Columns", "Status": status, "Details": details}
    return (len(missing) == 0), report_row


def check_column_pattern(df, col_name, pattern, check_name, dataset_name):
    """
    Checks if a string column matches a regex pattern (e.g., PLZ format).
    """
    if col_name not in df.columns:
        return {"Dataset": dataset_name, "Check": check_name, "Status": "SKIP", "Details": f"Column {col_name} missing"}

    # Convert to string, strip whitespace, apply regex.
    invalid_rows = df[~df[col_name].astype(str).str.strip().str.match(pattern)]

    return {
        "Dataset": dataset_name,
        "Check": check_name,
        "Status": "FAIL" if not invalid_rows.empty else "PASS",
        "Details": f"{len(invalid_rows)} rows failed pattern match",
    }


def check_numeric_condition(df, col_name, condition_func, check_name, dataset_name):
    """
    Checks if a numeric column satisfies a lambda condition (e.g., x > 0).
    """
    if col_name not in df.columns:
        return {"Dataset": dataset_name, "Check": check_name, "Status": "SKIP", "Details": f"Column {col_name} missing"}

    try:
        # Force numeric, coerce errors to NaN.
        numeric_series = pd.to_numeric(df[col_name], errors="coerce")

        # Check 1: Are there non-numbers?.
        nans = numeric_series.isna().sum()
        if nans > 0:
            return {
                "Dataset": dataset_name,
                "Check": check_name,
                "Status": "FAIL",
                "Details": f"{nans} non-numeric values found",
            }

        # Check 2: Apply the logical condition.
        invalid_rows = numeric_series[~numeric_series.apply(condition_func)]

        return {
            "Dataset": dataset_name,
            "Check": check_name,
            "Status": "FAIL" if not invalid_rows.empty else "PASS",
            "Details": f"{len(invalid_rows)} values failed condition",
        }
    except Exception as e:
        return {"Dataset": dataset_name, "Check": check_name, "Status": "ERROR", "Details": str(e)}


def validate_geo_dataset(df):
    results = []
    name = "Dataset A (Berlin Geo. PLZ)"

    # 1. Check Columns (Guard Clause).
    cols_ok, row = check_required_columns(df, ["PLZ", "geometry"], name)
    results.append(row)
    if not cols_ok:
        return results  # Stop if any column is missing.

    # 2. Check PLZ Format (5 Digits)
    results.append(check_column_pattern(df, "PLZ", r"^\d{5}$", "PLZ Format", name))

    # 3. Check Geometry integrity.
    missing_geo = df["geometry"].isnull().sum()
    results.append(
        {
            "Dataset": name,
            "Check": "Geometry Integrity",
            "Status": "FAIL" if missing_geo > 0 else "PASS",
            "Details": f"{missing_geo} missing geometries",
        }
    )

    return results


def validate_station_dataset(df):
    results = []
    name = "Dataset B (Stations)"
    req_cols = ["Postleitzahl", "Bundesland", "Breitengrad", "Längengrad", "Nennleistung Ladeeinrichtung [kW]"]

    # 1. Check Columns.
    cols_ok, row = check_required_columns(df, req_cols, name)
    results.append(row)
    if not cols_ok:
        return results

    # 2. Check PLZ.
    results.append(check_column_pattern(df, "Postleitzahl", r"^\d{5}$", "PLZ Format", name))

    # 3. Check Power > 0.
    results.append(
        check_numeric_condition(df, "Nennleistung Ladeeinrichtung [kW]", lambda x: x > 0, "Power > 0 kW", name)
    )

    # 4. Check Latitude (Berlin Bounds approx 52.3 - 52.7).
    results.append(check_numeric_condition(df, "Breitengrad", lambda x: 52.3 <= x <= 52.7, "Latitude (Berlin)", name))

    # 5. Check Longitude (Berlin Bounds approx 13.0 - 13.8)
    results.append(check_numeric_condition(df, "Längengrad", lambda x: 13.0 <= x <= 13.8, "Longitude (Berlin)", name))

    # 6. Check Scope (Bundesland) - Custom logic
    non_berlin = df[~df["Bundesland"].astype(str).str.contains("Berlin", case=False, na=False)]
    results.append(
        {
            "Dataset": name,
            "Check": "Scope (Bundesland)",
            "Status": "INFO" if not non_berlin.empty else "PASS",
            "Details": f"{len(non_berlin)} stations outside Berlin",
        }
    )

    return results


def validate_population_dataset(df):
    results = []
    name = "Dataset C (Population)"

    # 1. Check Columns
    cols_ok, row = check_required_columns(df, ["plz", "einwohner", "lat", "lon"], name)
    results.append(row)
    if not cols_ok:
        return results

    # 2. Check PLZ
    results.append(check_column_pattern(df, "plz", r"^\d{5}$", "PLZ Format", name))

    # 3. Check Population (Must be positive integer)
    results.append(check_numeric_condition(df, "einwohner", lambda x: x > 0, "Population > 0", name))

    return results


def analyze_distributions(df_stations, df_pop):
    """
    Calculates statistical metrics (Range, Mean, Median, Distribution)
    for relevant numeric columns to check for plausibility.
    """
    stats_list = []

    # 1. Define columns to analyze per dataset
    analysis_targets = [
        {
            "name": "Dataset B (Stations)",
            "df": df_stations,
            "cols": ["Nennleistung Ladeeinrichtung [kW]"],
        },
        {"name": "Dataset C (Population)", "df": df_pop, "cols": ["einwohner"]},
    ]

    for target in analysis_targets:
        df = target["df"]
        dataset_name = target["name"]

        for col in target["cols"]:
            if col not in df.columns:
                continue

            # Ensure numeric (drop NaNs for stats)
            series = pd.to_numeric(df[col], errors="coerce").dropna()

            if series.empty:
                continue

            # Calculate Metrics
            stats = {
                "Dataset": dataset_name,
                "Column": col,
                "Count": len(series),
                "Min": series.min(),
                "Max": series.max(),
                "Mean": round(series.mean(), 2),
                "Median": round(series.median(), 2),
                "Std Dev": round(series.std(), 2),
                "25% (Q1)": round(series.quantile(0.25), 2),
                "75% (Q3)": round(series.quantile(0.75), 2),
            }
            stats_list.append(stats)

    return pd.DataFrame(stats_list)


def run_audit_pipeline(df_geo, df_stations, df_pop):
    """
    Runs all validators and aggregates the report.
    """
    full_report = []

    full_report.extend(validate_geo_dataset(df_geo))
    full_report.extend(validate_station_dataset(df_stations))
    full_report.extend(validate_population_dataset(df_pop))

    return pd.DataFrame(full_report)


def preprocess_data(lstat_data, residents_data):
    # Filter out data specific to Berlin.
    lstat_data = lstat_data[
        (lstat_data["Bundesland"] == "Berlin")
        & (lstat_data["Postleitzahl"] > 10115)
        & (lstat_data["Postleitzahl"] < 14200)
    ]
    residents_data = residents_data[(residents_data["plz"] > 10000) & (residents_data["plz"] < 14200)]

    lstat_data.loc[:, "Nennleistung Ladeeinrichtung [kW]"] = (
        lstat_data["Nennleistung Ladeeinrichtung [kW]"].str.replace(",", ".").astype(float)
    )
    lstat_data.loc[:, "Breitengrad"] = lstat_data["Breitengrad"].str.replace(",", ".").astype(float)
    lstat_data.loc[:, "Längengrad"] = lstat_data["Längengrad"].str.replace(",", ".").astype(float)
    return lstat_data, residents_data


if __name__ == "__main__":
    # Load Data.
    geo_plz_data, lstat_data, residents_data = mt.load_datasets(pdict)

    # Filter out data specific to Berlin and basic data specific pre-processing.
    lstat_data, residents_data = preprocess_data(lstat_data, residents_data)

    quality_report = run_audit_pipeline(geo_plz_data, lstat_data, residents_data)
    print("\n--- Data Quality Audit ---")
    print(quality_report.to_markdown(index=False))

    # 2. Run the Statistical Analysis (Plausibility Check)
    stats_report = analyze_distributions(lstat_data, residents_data)
    print("\n--- Statistical Distribution Analysis ---")
    print(stats_report.to_markdown(index=False))
