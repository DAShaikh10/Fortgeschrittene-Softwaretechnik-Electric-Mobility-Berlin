import os
import folium
import pandas as pd
import streamlit as st
import geopandas as gpd
import pandas as pd
import core.helper_tools as ht
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from streamlit_folium import folium_static
from branca.colormap import LinearColormap


def sort_by_plz_add_geometry(dfr: pd.DataFrame, dfg: pd.DataFrame, pdict: dict) -> gpd.GeoDataFrame:
    """
    Sort a DataFrame by postal code (PLZ) and add geometric data from a reference GeoDataFrame.
    This function takes a regular DataFrame and merges it with a GeoDataFrame containing
    geometric information based on a postal code field. The resulting DataFrame is sorted
    by PLZ, cleaned of entries without geometry, and returned as a GeoDataFrame.
    Args:
        dfr (pd.DataFrame): The input DataFrame containing data to be sorted and enriched
            with geometric information. Must contain a column matching the geocode key.
        dfg (pd.DataFrame): A DataFrame containing geometric data with columns matching
            the geocode key and a 'geometry' column with WKT (Well-Known Text) representations.
        pdict (dict): A dictionary containing configuration parameters. Must include a
            'geocode' key that specifies the column name to merge on (typically 'PLZ').
    Returns:
        gpd.GeoDataFrame: A GeoDataFrame sorted by PLZ with geometric data added.
            Rows without valid geometry are excluded. The geometry column is converted
            from WKT format to proper geometric objects.
    """
    dframe = dfr.copy()
    df_geo = dfg.copy()

    sorted_df = dframe.sort_values(by="PLZ").reset_index(drop=True).sort_index()

    # We can simply use `inner` join instead of left join followed by dropna.
    # sorted_df2 = sorted_df.merge(df_geo, on=pdict["geocode"], how="left")
    # sorted_df3 = sorted_df2.dropna(subset=["geometry"])

    sorted_df3 = sorted_df.merge(df_geo, on=pdict["geocode"], how="inner")

    sorted_df3["geometry"] = gpd.GeoSeries.from_wkt(sorted_df3["geometry"])
    ret = gpd.GeoDataFrame(sorted_df3, geometry="geometry")

    return ret


# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr: pd.DataFrame, dfg: pd.DataFrame, pdict: dict) -> gpd.GeoDataFrame:
    """
    Preprocessing dataframe from `Ladesaeulenregister.csv`
    """

    dframe = dfr.copy()
    df_geo = dfg.copy()

    # These are the columns which we will use from the Ladesaeulenregister dataset.
    # NOTE: This helps answer Task requirements as layed out on LMS.
    # i.e. What are necessary columns?
    # Answer: (Partial) - Postleitzahl -> PLZ, Bundesland, Breitengrad, Längengrad, Nennleistung Ladeeinrichtung [kW] -> KW
    dframe2 = dframe.loc[
        :,
        [
            "Postleitzahl",
            "Bundesland",
            "Breitengrad",
            "Längengrad",
            "Nennleistung Ladeeinrichtung [kW]",
        ],
    ]
    dframe2.rename(
        columns={"Nennleistung Ladeeinrichtung [kW]": "KW", "Postleitzahl": "PLZ"},
        inplace=True,  # In-place and hence no reassignment needed.
    )

    # Convert to string.
    dframe2["Breitengrad"] = dframe2["Breitengrad"].astype(str)
    dframe2["Längengrad"] = dframe2["Längengrad"].astype(str)

    # Now replace the commas with periods.
    dframe2["Breitengrad"] = dframe2["Breitengrad"].str.replace(",", ".")
    dframe2["Längengrad"] = dframe2["Längengrad"].str.replace(",", ".")

    # Here, the code explicitly filters out only Berlin entries and hence we do not need to handle the same.
    dframe3 = dframe2[(dframe2["Bundesland"] == "Berlin") & (dframe2["PLZ"] > 10115) & (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)

    return ret


# -----------------------------------------------------------------------------
@ht.timer
def count_plz_occurrences(df_lstat2: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Counts the number of loading stations per postal code (PLZ) area.

    This function aggregates charging station data by grouping entries that share
    the same PLZ (Postleitzahl - German postal code) and counts how many stations
    exist in each postal code area. It preserves geometric information by taking
    the first geometry object from each PLZ group.

    Args:
        df_lstat2 (gpd.GeoDataFrame): A GeoDataFrame containing preprocessed charging
            station data. Must include:
            - 'PLZ' column: Postal codes (integers) for grouping
            - 'geometry' column: Geometric data representing station locations or
              postal code boundaries

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with aggregated results containing:
            - 'PLZ' column: Unique postal codes
            - 'Number' column: Count of charging stations per PLZ
            - 'geometry' column: The first geometry object from each PLZ group

    Notes:
        - The geometry aggregation uses 'first', which assumes all stations in the
          same PLZ share similar or relevant geometry. This works when the input
          geometry represents PLZ boundaries rather than individual station points.
        - The reset_index() call ensures PLZ becomes a regular column instead of
          remaining as the DataFrame index.
    """

    # Group by PLZ and count occurrences, keeping geometry.
    result_df = df_lstat2.groupby("PLZ").agg(Number=("PLZ", "count"), geometry=("geometry", "first")).reset_index()

    return result_df


# -----------------------------------------------------------------------------
@ht.timer
def count_plz_by_power_category(df_lstat2: pd.DataFrame):
    """
    Counts loading stations per PLZ categorized by power rating (kW).

    Categories:
    - Slow: < 11 kW
    - Normal: 11-22 kW
    - Fast: 22-50 kW
    - Rapid: 50-150 kW
    - Ultra-rapid: >= 150 kW

    Returns:
        Dictionary with DataFrames for each category and total
    """
    df = df_lstat2.copy()

    # Convert KW to numeric
    df["KW_numeric"] = pd.to_numeric(df["KW"], errors="coerce")

    # Remove rows with invalid KW values
    df = df.dropna(subset=["KW_numeric"])

    # Define power categories
    def categorize_power(kw):
        if kw < 11:
            return "Slow"
        elif kw < 22:
            return "Normal"
        elif kw < 50:
            return "Fast"
        elif kw < 150:
            return "Rapid"
        else:
            return "Ultra-rapid"

    df["Power_Category"] = df["KW_numeric"].apply(categorize_power)

    # Group by PLZ and power category
    result_dict = {}

    # Total count (same as count_plz_occurrences)
    result_dict["Total"] = df.groupby("PLZ").agg(Number=("PLZ", "count"), geometry=("geometry", "first")).reset_index()

    # Count by category
    categories = ["Slow", "Normal", "Fast", "Rapid", "Ultra-rapid"]
    for category in categories:
        df_category = df[df["Power_Category"] == category]
        if len(df_category) > 0:
            result_dict[category] = (
                df_category.groupby("PLZ").agg(Number=("PLZ", "count"), geometry=("geometry", "first")).reset_index()
            )
        else:
            # Empty dataframe with correct structure
            result_dict[category] = gpd.GeoDataFrame(columns=["PLZ", "Number", "geometry"])

    return result_dict


# -----------------------------------------------------------------------------
# NOTE: This is to answer the sub-task #9:
# Additional task (not evaluated): Make separate layers for each KW.
@ht.timer
def count_plz_occurrences_by_kw(df_lstat2: gpd.GeoDataFrame) -> dict[str, gpd.GeoDataFrame]:
    """
    Counts the number of loading stations per postal code (PLZ) area, grouped by power capacity (KW).

    This function creates separate aggregations for different KW ranges, allowing for
    layered visualizations based on charging station power capacity.

    Args:
        df_lstat2 (gpd.GeoDataFrame): A GeoDataFrame containing preprocessed charging
            station data with 'PLZ', 'KW', and 'geometry' columns.

    Returns:
        dict[str, gpd.GeoDataFrame]: A dictionary where keys are KW range labels and
            values are GeoDataFrames with counts per PLZ for that KW range.
    """
    # Define KW ranges.
    # NOTE: The ranges are defined manually and can be better defined with domain reference.
    kw_ranges = {
        "Slow (≤22 kW)": (0, 22),
        "Fast (22-50 kW)": (22, 50),
        "Rapid (50-150 kW)": (50, 150),
        "Ultra (>150 kW)": (150, float("inf")),
    }

    result_dict = {}

    # Ensure KW is numeric for filtering.
    df_lstat2 = df_lstat2.copy()
    df_lstat2["KW"] = pd.to_numeric(df_lstat2["KW"], errors="coerce")
    df_lstat2 = df_lstat2.dropna(subset=["KW"])

    for label, (min_kw, max_kw) in kw_ranges.items():
        # Build mask respecting inclusive upper bound and exclusive lower (except first range).
        if label.startswith("Slow"):
            mask = df_lstat2["KW"] <= max_kw
        else:
            mask = (df_lstat2["KW"] > min_kw) & (df_lstat2["KW"] <= max_kw)

        filtered_df = df_lstat2[mask]

        # Group by PLZ and count.
        if not filtered_df.empty:
            grouped = (
                filtered_df.groupby("PLZ").agg(Number=("PLZ", "count"), geometry=("geometry", "first")).reset_index()
            )
            result_dict[label] = grouped

    return result_dict


# -----------------------------------------------------------------------------
@ht.timer
def preprop_resid(dfr: pd.DataFrame, dfg: gpd.GeoDataFrame, pdict: dict) -> gpd.GeoDataFrame:
    """
    Preprocess residential data by filtering and transforming postal code information.
    This function takes a DataFrame containing postal code and population data,
    filters it for Berlin postal codes (10000-14200), transforms coordinate formats,
    and merges it with geographical data.

    Args:
        dfr (pd.DataFrame): DataFrame containing residential data with columns:
            - plz: postal code
            - einwohner: number of inhabitants
            - lat: latitude (may contain commas as decimal separators)
            - lon: longitude (may contain commas as decimal separators)
        dfg (gpd.GeoDataFrame): GeoDataFrame containing geographical boundary data
            for postal code regions
        pdict (dict): Dictionary parameter passed to sort_by_plz_add_geometry function,
            likely containing postal code mapping or configuration data
    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with processed residential data including:
            - PLZ: postal code
            - Einwohner: population count
            - Breitengrad: latitude (converted to float format)
            - Längengrad: longitude (converted to float format)
            - Geometry information from the geographical DataFrame
    """

    dframe = dfr.copy()
    df_geo = dfg.copy()

    # These are the columns which we will use from the plz_einwohner dataset.
    # NOTE: This helps answer Task requirements as layed out on LMS.
    # i.e. What are necessary columns?
    # Answer: (Partial) - plz -> PLZ, Einwohner, lat -> Breitengrad, lon -> Längengrad
    dframe2 = dframe.loc[:, ["plz", "einwohner", "lat", "lon"]]
    dframe2.rename(
        columns={
            "plz": "PLZ",
            "einwohner": "Einwohner",
            "lat": "Breitengrad",
            "lon": "Längengrad",
        },
        inplace=True,
    )

    # Convert to string.
    dframe2["Breitengrad"] = dframe2["Breitengrad"].astype(str)
    dframe2["Längengrad"] = dframe2["Längengrad"].astype(str)

    # Now replace the commas with periods.
    dframe2["Breitengrad"] = dframe2["Breitengrad"].str.replace(",", ".")
    dframe2["Längengrad"] = dframe2["Längengrad"].str.replace(",", ".")

    # Here, the code explicitly filters out only Berlin entries and hence we do not need to handle the same.
    dframe3 = dframe2[(dframe2["PLZ"] > 10000) & (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)

    return ret


# -----------------------------------------------------------------------------
def setup_sidebar_search(dframe1: gpd.GeoDataFrame, dframe2: gpd.GeoDataFrame):
    """
    Setup postal code search in sidebar and return selected PLZ with info.
    """

    st.sidebar.markdown("---")
    st.sidebar.subheader("📍 Search by Postal Code")

    all_plz = sorted(set(dframe1["PLZ"].tolist() + dframe2["PLZ"].tolist()))

    search_plz = st.sidebar.selectbox(
        "Select PLZ:", options=[""] + all_plz, format_func=lambda x: "All areas" if x == "" else str(int(x))
    )

    plz_info = {}
    if search_plz != "":
        if search_plz in dframe1["PLZ"].values:
            plz_info["stations"] = int(dframe1[dframe1["PLZ"] == search_plz].iloc[0]["Number"])
        if search_plz in dframe2["PLZ"].values:
            plz_info["population"] = int(dframe2[dframe2["PLZ"] == search_plz].iloc[0]["Einwohner"])

        if plz_info:
            info_parts = []
            if "population" in plz_info:
                info_parts.append(f"👥 Pop: {plz_info['population']:,}")
            if "stations" in plz_info:
                info_parts.append(f"⚡ Stations: {plz_info['stations']}")
            st.sidebar.info("\n\n".join(info_parts))

    return search_plz, plz_info


# -----------------------------------------------------------------------------
def get_map_center_and_zoom(search_plz, dframe1: gpd.GeoDataFrame, dframe2: gpd.GeoDataFrame):
    """
    Calculate map center and zoom level based on selected postal code.
    """

    if search_plz == "":
        return [52.52, 13.40], 10

    plz_geometry = None
    if search_plz in dframe1["PLZ"].values:
        plz_geometry = dframe1[dframe1["PLZ"] == search_plz].iloc[0]["geometry"]
    elif search_plz in dframe2["PLZ"].values:
        plz_geometry = dframe2[dframe2["PLZ"] == search_plz].iloc[0]["geometry"]

    if plz_geometry:
        centroid = plz_geometry.centroid
        return [centroid.y, centroid.x], 13

    return [52.52, 13.40], 10


# -----------------------------------------------------------------------------
def setup_view_mode_selection(dfr_by_kw: dict):
    """
    Setup visualization mode and layer selection in sidebar.
    """

    st.sidebar.markdown("---")
    view_mode = st.sidebar.radio("Visualization Mode", ["Basic View", "Power Capacity (KW) View"])

    if view_mode == "Basic View":
        layer_options = ["Residents", "All Charging Stations"]
    else:
        layer_options = ["Residents"]
        if dfr_by_kw:
            layer_options.extend(list(dfr_by_kw.keys()))

    st.sidebar.header("📊 Layer Selection")
    layer_selection = st.sidebar.radio("Select Layer", layer_options)

    return view_mode, layer_selection


# -----------------------------------------------------------------------------
def render_residents_layer(m, dframe2: gpd.GeoDataFrame, search_plz):
    """
    Add residents heatmap layer to the map.
    """

    color_map = LinearColormap(
        colors=["yellow", "red"],
        vmin=dframe2["Einwohner"].min(),
        vmax=dframe2["Einwohner"].max(),
    )

    for _, row in dframe2.iterrows():
        is_selected = search_plz != "" and row["PLZ"] == search_plz
        folium.GeoJson(
            row["geometry"],
            style_function=lambda _, color=color_map(row["Einwohner"]), is_sel=is_selected: {
                "fillColor": color,
                "color": "blue" if is_sel else "black",
                "weight": 4 if is_sel else 1,
                "fillOpacity": 0.9 if is_sel else 0.7,
            },
            tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}" + (" ⭐ SELECTED" if is_selected else ""),
        ).add_to(m)

    color_map.add_to(m)


# -----------------------------------------------------------------------------
def render_charging_stations_layer(m, dframe1: gpd.GeoDataFrame, search_plz):
    """
    Add charging stations heatmap layer to the map.
    """

    color_map = LinearColormap(
        colors=["yellow", "red"],
        vmin=dframe1["Number"].min(),
        vmax=dframe1["Number"].max(),
    )

    for _, row in dframe1.iterrows():
        is_selected = search_plz != "" and row["PLZ"] == search_plz
        folium.GeoJson(
            row["geometry"],
            style_function=lambda _, color=color_map(row["Number"]), is_sel=is_selected: {
                "fillColor": color,
                "color": "blue" if is_sel else "black",
                "weight": 4 if is_sel else 1,
                "fillOpacity": 0.9 if is_sel else 0.7,
            },
            tooltip=f"PLZ: {row['PLZ']}, Number: {row['Number']}" + (" ⭐ SELECTED" if is_selected else ""),
        ).add_to(m)

    color_map.add_to(m)


# -----------------------------------------------------------------------------
def render_kw_layer(m, df_kw: gpd.GeoDataFrame, layer_name: str, search_plz):
    """
    Add power capacity specific layer to the map.
    """

    color_map = LinearColormap(
        colors=["yellow", "red"],
        vmin=df_kw["Number"].min(),
        vmax=df_kw["Number"].max(),
    )

    for _, row in df_kw.iterrows():
        is_selected = search_plz != "" and row["PLZ"] == search_plz
        folium.GeoJson(
            row["geometry"],
            style_function=lambda _, color=color_map(row["Number"]), is_sel=is_selected: {
                "fillColor": color,
                "color": "blue" if is_sel else "black",
                "weight": 4 if is_sel else 1,
                "fillOpacity": 0.9 if is_sel else 0.7,
            },
            tooltip=f"PLZ: {row['PLZ']}, Stations: {row['Number']} ({layer_name})"
            + (" ⭐ SELECTED" if is_selected else ""),
        ).add_to(m)

    color_map.add_to(m)


# -----------------------------------------------------------------------------
def create_demand_priority_map(demand_analysis: gpd.GeoDataFrame, map_center, map_zoom, search_plz) -> folium.Map:
    """
    Create a separate map showing demand priority analysis.
    """

    demand_map = folium.Map(location=map_center, zoom_start=map_zoom)

    priority_colors = {"CRITICAL": "#d32f2f", "HIGH": "#ff9800", "MEDIUM": "#fbc02d", "LOW": "#388e3c"}

    for _, row in demand_analysis.iterrows():
        is_selected = search_plz != "" and row["PLZ"] == search_plz
        color = priority_colors.get(row["Demand_Priority"], "#888888")

        ratio_text = (
            f"{row['Residents_per_Station']:.1f}" if row["Residents_per_Station"] != float("inf") else "No stations"
        )

        tooltip_html = f"""
        <div style="font-family: Arial; font-size: 12px;">
            <b>PLZ:</b> {row['PLZ']}<br>
            <b>Priority:</b> {row['Demand_Priority']}<br>
            <b>Population:</b> {int(row['Einwohner']):,}<br>
            <b>Stations:</b> {int(row['Number'])}<br>
            <b>Residents/Station:</b> {ratio_text}
        </div>
        """

        folium.GeoJson(
            row["geometry"],
            style_function=lambda _, color=color, is_sel=is_selected: {
                "fillColor": color,
                "color": "blue" if is_sel else "black",
                "weight": 4 if is_sel else 1,
                "fillOpacity": 0.9 if is_sel else 0.7,
            },
            tooltip=folium.Tooltip(tooltip_html),
        ).add_to(demand_map)

    # Add legend
    legend_html = """
    <div style="position: fixed; top: 10px; right: 10px; width: 200px;
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
        <p style="margin: 0 0 10px 0; font-weight: bold;">Demand Priority</p>
        <p style="margin: 5px 0;"><span style="background-color: #d32f2f; padding: 3px 10px; border-radius: 3px; color: white;">■</span> CRITICAL</p>
        <p style="margin: 5px 0;"><span style="background-color: #ff9800; padding: 3px 10px; border-radius: 3px; color: white;">■</span> HIGH</p>
        <p style="margin: 5px 0;"><span style="background-color: #fbc02d; padding: 3px 10px; border-radius: 3px; color: black;">■</span> MEDIUM</p>
        <p style="margin: 5px 0;"><span style="background-color: #388e3c; padding: 3px 10px; border-radius: 3px; color: white;">■</span> LOW</p>
    </div>
    """
    demand_map.get_root().html.add_child(folium.Element(legend_html))

    return demand_map


# -----------------------------------------------------------------------------
def display_priority_summary(demand_analysis: gpd.GeoDataFrame, search_plz):
    """
    Display summary cards for priority distribution.
    """

    st.subheader("Priority Distribution" + (f" for PLZ {int(search_plz)}" if search_plz != "" else ""))

    col1, col2, col3, col4 = st.columns(4)

    priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    emojis = ["🔴", "🟠", "🟡", "🟢"]
    helps = [
        "Pop > 15K, Stations < 10",
        "Pop > 15K, Stations 10-20",
        "Pop 8K-15K, Stations < 10",
        "Well-served or low demand",
    ]

    for col, priority, emoji, help_text in zip([col1, col2, col3, col4], priorities, emojis, helps):
        with col:
            count = len(demand_analysis[demand_analysis["Demand_Priority"] == priority])
            st.metric(f"{emoji} {priority}", count, help=help_text)


# -----------------------------------------------------------------------------
def display_analysis_table(demand_analysis: gpd.GeoDataFrame, search_plz):
    """
    Display filterable and sortable demand analysis table.
    """
    st.subheader("📋 Detailed Analysis Table")

    col1, col2, col3 = st.columns(3)

    with col1:
        default_priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"] if search_plz != "" else ["CRITICAL", "HIGH"]
        priority_filter = st.multiselect(
            "Filter by Priority", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=default_priorities
        )

    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Residents_per_Station", "Einwohner", "Number"],
            format_func=lambda x: {
                "Residents_per_Station": "Residents/Station",
                "Einwohner": "Population",
                "Number": "Station Count",
            }[x],
        )

    with col3:
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)

    display_data = demand_analysis[demand_analysis["Demand_Priority"].isin(priority_filter)].copy()

    if not display_data.empty:
        display_data["Residents_per_Station"] = display_data["Residents_per_Station"].replace(float("inf"), 999999)
        display_data = display_data.sort_values(by=sort_by, ascending=(sort_order == "Ascending"))

        display_data["Residents_per_Station_Display"] = display_data["Residents_per_Station"].apply(
            lambda x: "No stations" if x >= 999999 else f"{x:.1f}"
        )

        st.dataframe(
            display_data[["PLZ", "Einwohner", "Number", "Residents_per_Station_Display", "Demand_Priority"]].rename(
                columns={
                    "PLZ": "Postal Code",
                    "Einwohner": "Population",
                    "Number": "Charging Stations",
                    "Residents_per_Station_Display": "Residents/Station",
                    "Demand_Priority": "Priority",
                }
            ),
            use_container_width=True,
            height=500,
        )

        csv = display_data[["PLZ", "Einwohner", "Number", "Residents_per_Station", "Demand_Priority"]].to_csv(
            index=False
        )
        csv_filename = f"demand_analysis_PLZ_{int(search_plz)}.csv" if search_plz != "" else "demand_analysis.csv"
        st.download_button(label="📥 Download CSV", data=csv, file_name=csv_filename, mime="text/csv")
    else:
        st.info("No data matches the selected filters.")


# -----------------------------------------------------------------------------
def display_methodology():
    """
    Display methodology explanation in expander.
    """

    with st.expander("How is Priority Calculated?"):
        st.markdown(
            """
        **Priority Classification:**

        - **🔴 CRITICAL**: Pop > 15K, Stations < 10 -> Immediate action
        - **🟠 HIGH**: Pop > 15K, Stations 10-20 -> Short-term planning
        - **🟡 MEDIUM**: Pop 8K-15K, Stations < 10 -> Medium-term planning
        - **🟢 LOW**: Pop < 8K or Stations > 20 -> Monitor

                **Data Ranges:** Population (139-35,535), Stations (1-105)
        """
        )


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_charging_resid(
    dfr1: gpd.GeoDataFrame, dfr2: gpd.GeoDataFrame, dfr_by_kw: dict = None, demand_analysis: gpd.GeoDataFrame = None
):
    """
    Main Streamlit app displaying interactive maps of Berlin's EV infrastructure.

    Shows heatmaps of charging stations and population density with options to:
    - Filter by power capacity
    - Search specific postal codes
    - View demand priority analysis
    """
    dframe1 = dfr1.copy()
    dframe2 = dfr2.copy()

    st.set_page_config(layout="wide", page_title="Berlin EV Infrastructure")
    st.title("Berlin Electric Vehicle Infrastructure Analysis")

    # Sidebar setup.
    st.sidebar.header("🔍 View Options")
    search_plz, _ = setup_sidebar_search(dframe1, dframe2)
    _, layer_selection = setup_view_mode_selection(dfr_by_kw)

    # Demand analysis toggle.
    show_demand = False
    if demand_analysis is not None:
        st.sidebar.markdown("---")
        show_demand = st.sidebar.checkbox("📈 Show Demand Analysis", value=False)

    # Create main map.
    map_center, map_zoom = get_map_center_and_zoom(search_plz, dframe1, dframe2)
    m = folium.Map(location=map_center, zoom_start=map_zoom)

    # Render selected layer.
    if layer_selection == "Residents":
        render_residents_layer(m, dframe2, search_plz)
    elif layer_selection == "All Charging Stations":
        render_charging_stations_layer(m, dframe1, search_plz)
    else:
        if dfr_by_kw and layer_selection in dfr_by_kw:
            render_kw_layer(m, dfr_by_kw[layer_selection], layer_selection, search_plz)

    folium_static(m, width=1400, height=800)

    # Show demand analysis if enabled
    if show_demand and demand_analysis is not None:
        st.markdown("---")
        st.header("📊 Demand Priority Analysis")

        # Filter by selected PLZ if applicable
        filtered_demand = demand_analysis.copy()
        if search_plz != "":
            plz_filtered = demand_analysis[demand_analysis["PLZ"] == search_plz]
            if not plz_filtered.empty:
                st.info(f"📍 Showing analysis for PLZ: **{int(search_plz)}**")
                filtered_demand = plz_filtered
            else:
                st.warning(f"No data for PLZ: {int(search_plz)}")

        display_priority_summary(filtered_demand, search_plz)

        st.markdown("---")
        st.subheader("🗺️ Demand Priority Map")
        demand_map = create_demand_priority_map(filtered_demand, map_center, map_zoom, search_plz)
        folium_static(demand_map, width=1400, height=800)

        st.markdown("---")
        display_analysis_table(filtered_demand, search_plz)
        display_methodology()


# -----------------------------------------------------------------------------
def load_datasets(pdict) -> tuple[pd.DataFrame]:
    """
    Loads the required datasets for the application.

    Returns:
        tuple[pd.DataFrame]: A tuple containing the loaded dataframes in the order:
                             (geodata_berlin_plz, Ladesaeulenregister, plz_einwohner)
    """
    cwd = os.getcwd()

    # Determine the 'geodata_berlin_plz' dataset path.
    geodat_plz_file_path = os.path.join(cwd, pdict["dataset_folder"], pdict["file_geodat_plz"])

    # Determine the 'Ladesaeulenregister' dataset path.
    lstat_file_path = os.path.join(cwd, pdict["dataset_folder"], pdict["file_lstations"])

    # Determine the 'plz_einwohner' dataset path.
    resid_file_path = os.path.join(cwd, pdict["dataset_folder"], pdict["file_residents"])

    # Load datasets.
    df_geodat_plz = pd.read_csv(geodat_plz_file_path, delimiter=";")

    # The Ladesäulenregister CSV file uses Windows-1252 encoding (And not utf-8!) and has 10 header rows to skip.
    # Also, requires to set low_memory to False as the dataset is relatively large.
    df_lstat = pd.read_csv(lstat_file_path, encoding="Windows-1252", sep=";", low_memory=False, skiprows=10)
    df_residents = pd.read_csv(resid_file_path, sep=",")

    return (df_geodat_plz, df_lstat, df_residents)


# -----------------------------------------------------------------------------
@ht.timer
def calculate_demand_priority(gdf_residents: gpd.GeoDataFrame, gdf_stations: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Calculate demand priority for additional charging stations based on population and existing infrastructure.

    Priority Classification:
    Data ranges: Population (139-35,535), Stations (1-105) (Last year (2024) the max was 95!)

    - CRITICAL: Population > 15,000 AND Stations < 10 (Ratio > 1,500)
    - HIGH: Population > 15,000 AND Stations 10-20 (Ratio 750-1,500)
    - MEDIUM: Population 8,000-15,000 AND Stations < 10
    - LOW: Population < 8,000 OR Stations > 20

    Args:
        gdf_residents (gpd.GeoDataFrame): GeoDataFrame with 'PLZ' and 'Einwohner' columns
        gdf_stations (gpd.GeoDataFrame): GeoDataFrame with 'PLZ' and 'Number' columns

    Returns:
        gpd.GeoDataFrame: Merged data with demand priority classification including:
            - PLZ: Postal code
            - Einwohner: Population
            - Number: Current charging stations
            - Residents_per_Station: Ratio metric (Population / Stations)
            - Demand_Priority: CRITICAL/HIGH/MEDIUM/LOW classification
    """
    # Merge datasets.
    merged = gdf_residents.merge(gdf_stations[["PLZ", "Number"]], on="PLZ", how="left")
    merged["Number"] = merged["Number"].fillna(0)  # PLZ with no stations.

    # Calculate residents per station ratio.
    merged["Residents_per_Station"] = merged.apply(
        lambda row: row["Einwohner"] / row["Number"] if row["Number"] > 0 else float("inf"), axis=1
    )

    # Define thresholds based on actual data distribution statistics.
    POP_HIGH = 15000  # Top ~25% of population density.
    POP_MEDIUM = 8000  # Middle 50% threshold.
    STATIONS_LOW = 10  # ~10% of maximum stations
    STATIONS_MEDIUM = 20  # ~20% of maximum stations.

    # Classify demand priority.
    def classify_demand(row):
        pop = row["Einwohner"]
        stations = row["Number"]

        if pop > POP_HIGH and stations < STATIONS_LOW:
            return "CRITICAL"
        elif pop > POP_HIGH and stations < STATIONS_MEDIUM:
            return "HIGH"
        elif pop > POP_MEDIUM and stations < STATIONS_LOW:
            return "MEDIUM"
        else:
            return "LOW"

    merged["Demand_Priority"] = merged.apply(classify_demand, axis=1)  # Axis = 1 - Column-wise operation.

    return merged


# -----------------------------------------------------------------------------
@ht.timer
def demand_analysis_summary(demand_analysis: gpd.GeoDataFrame):
    """
    Print a summary of demand priority analysis for electric charging stations in Berlin.

    This analysis will show up as an toggleable section in the Streamlit app.

    Args:
        demand_analysis (gpd.GeoDataFrame): GeoDataFrame containing demand analysis results
            with columns: PLZ, Einwohner, Number, Residents_per_Station, Demand_Priority.
    """

    # Sub-task #7: Analyze both geovisualizations: Where do you see demand for additional electric charging stations?
    print("\n" + "=" * 80)
    print("DEMAND PRIORITY ANALYSIS FOR EV CHARGING STATIONS IN BERLIN")
    print("=" * 80)

    for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        priority_df = demand_analysis[demand_analysis["Demand_Priority"] == priority]
        print(f"\n{priority} Priority Areas: {len(priority_df)} postal codes")

        if not priority_df.empty:
            print(f"{'PLZ':<8} {'Population':<12} {'Stations':<10} {'Residents/Station':<20}")
            print("-" * 60)

            # Show top 5 for each priority.
            for _, row in priority_df.head(5).iterrows():
                ratio = (
                    f"{row['Residents_per_Station']:.1f}"
                    if row["Residents_per_Station"] != float("inf")
                    else "No stations"
                )
                print(f"{row['PLZ']:<8} {int(row['Einwohner']):<12} {int(row['Number']):<10} {ratio:<20}")

            if len(priority_df) > 5:
                print(f"... and {len(priority_df) - 5} more")

    print("\n" + "=" * 80 + "\n")


# -----------------------------------------------------------------------------
@ht.timer
def analyze_data_quality_and_outliers(
    df_geodat_plz: pd.DataFrame,
    df_lstat: pd.DataFrame,
    df_residents: pd.DataFrame,
    gdf_lstat3: gpd.GeoDataFrame = None,
    gdf_residents2: gpd.GeoDataFrame = None,
):
    """
    Generate comprehensive visualizations to identify anomalies, outliers, and data quality issues.

    Creates the following plots:
    1. Distribution plots for key numerical variables
    2. Box plots to identify outliers
    3. Correlation heatmaps
    4. Missing data analysis
    5. Statistical summaries

    Args:
        df_geodat_plz: Raw geodata for Berlin postal codes
        df_lstat: Raw charging stations data
        df_residents: Raw residents data
        gdf_lstat3: Processed charging stations geodataframe (optional)
        gdf_residents2: Processed residents geodataframe (optional)
    """

    print("\n" + "=" * 80)
    print("DATA QUALITY ANALYSIS & OUTLIER DETECTION")
    print("=" * 80 + "\n")

    # Set style for better looking plots
    sns.set_style("whitegrid")
    plt.rcParams["figure.figsize"] = (15, 10)

    # ========== 1. CHARGING STATIONS DATA ANALYSIS ==========
    print("=" * 80)
    print("1. CHARGING STATIONS DATA ANALYSIS")
    print("=" * 80)

    # Filter Berlin data
    df_lstat_berlin = df_lstat[
        (df_lstat["Bundesland"] == "Berlin") & (df_lstat["Postleitzahl"] > 10115) & (df_lstat["Postleitzahl"] < 14200)
    ].copy()

    # Convert KW to numeric
    df_lstat_berlin["KW_numeric"] = pd.to_numeric(df_lstat_berlin["Nennleistung Ladeeinrichtung [kW]"], errors="coerce")

    # Missing data analysis
    print("\n--- Missing Data in Charging Stations ---")
    missing_lstat = (
        df_lstat_berlin[["Postleitzahl", "Bundesland", "Breitengrad", "Längengrad", "KW_numeric"]].isnull().sum()
    )
    print(missing_lstat)
    print(f"\nTotal records: {len(df_lstat_berlin)}")
    print(f"Records with valid KW: {df_lstat_berlin['KW_numeric'].notna().sum()}")

    # Statistical summary for KW
    print("\n--- Statistical Summary: Power Capacity (KW) ---")
    print(df_lstat_berlin["KW_numeric"].describe())

    # Identify outliers using IQR method
    Q1 = df_lstat_berlin["KW_numeric"].quantile(0.25)
    Q3 = df_lstat_berlin["KW_numeric"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    outliers_kw = df_lstat_berlin[
        (df_lstat_berlin["KW_numeric"] < lower_bound) | (df_lstat_berlin["KW_numeric"] > upper_bound)
    ]
    print(f"\n--- Outliers in Power Capacity (IQR method) ---")
    print(f"Number of outliers: {len(outliers_kw)} ({len(outliers_kw)/len(df_lstat_berlin)*100:.2f}%)")
    print(f"Outlier range: < {lower_bound:.2f} or > {upper_bound:.2f}")

    # Create figure for charging stations analysis
    fig1, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig1.suptitle("Charging Stations Data Quality Analysis", fontsize=16, fontweight="bold")

    # Plot 1: Distribution of Power Capacity
    ax1 = axes[0, 0]
    df_lstat_berlin["KW_numeric"].dropna().hist(bins=50, ax=ax1, edgecolor="black")
    ax1.set_title("Distribution of Power Capacity (KW)")
    ax1.set_xlabel("Power (KW)")
    ax1.set_ylabel("Frequency")
    ax1.axvline(df_lstat_berlin["KW_numeric"].mean(), color="red", linestyle="--", label="Mean")
    ax1.axvline(df_lstat_berlin["KW_numeric"].median(), color="green", linestyle="--", label="Median")
    ax1.legend()
    # Plot 2: Box plot for Power Capacity
    ax2 = axes[0, 1]
    df_lstat_berlin.boxplot(column="KW_numeric", ax=ax2)
    ax2.set_title("Box Plot: Power Capacity Outliers")
    ax2.set_ylabel("Power (KW)")

    # Plot 3: Power Capacity by Category
    ax3 = axes[0, 2]
    df_lstat_berlin_copy = df_lstat_berlin.copy()
    df_lstat_berlin_copy["Power_Category"] = pd.cut(
        df_lstat_berlin_copy["KW_numeric"],
        bins=[0, 11, 22, 50, 150, float("inf")],
        labels=["Slow (<11)", "Normal (11-22)", "Fast (22-50)", "Rapid (50-150)", "Ultra (>150)"],
    )
    category_counts = df_lstat_berlin_copy["Power_Category"].value_counts()
    category_counts.plot(kind="bar", ax=ax3, color="steelblue", edgecolor="black")
    ax3.set_title("Distribution by Power Category")
    ax3.set_xlabel("Category")
    ax3.set_ylabel("Count")
    ax3.tick_params(axis="x", rotation=45)

    # Plot 4: Stations per PLZ (if processed data available)
    ax4 = axes[1, 0]
    if gdf_lstat3 is not None:
        gdf_lstat3["Number"].hist(bins=30, ax=ax4, edgecolor="black", color="coral")
        ax4.set_title("Stations per Postal Code")
        ax4.set_xlabel("Number of Stations")
        ax4.set_ylabel("Frequency")

        # Statistical summary
        print("\n--- Statistical Summary: Stations per PLZ ---")
        print(gdf_lstat3["Number"].describe())

        # Identify PLZ with unusually high/low station counts
        mean_stations = gdf_lstat3["Number"].mean()
        std_stations = gdf_lstat3["Number"].std()
        high_station_plz = gdf_lstat3[gdf_lstat3["Number"] > mean_stations + 2 * std_stations]
        low_station_plz = gdf_lstat3[gdf_lstat3["Number"] < 3]

        print(f"\nPLZ with unusually HIGH station count (> mean + 2σ):")
        print(high_station_plz[["PLZ", "Number"]].to_string(index=False))

        print(f"\nPLZ with LOW station count (< 3):")
        print(low_station_plz[["PLZ", "Number"]].to_string(index=False))
    else:
        ax4.text(0.5, 0.5, "Processed data not available", ha="center", va="center", transform=ax4.transAxes)
        ax4.set_title("Stations per Postal Code")

    # Plot 5: Missing data visualization
    ax5 = axes[1, 1]
    missing_pct = missing_lstat / len(df_lstat_berlin) * 100
    missing_pct.plot(kind="bar", ax=ax5, color="indianred", edgecolor="black")
    ax5.set_title("Missing Data Percentage")
    ax5.set_ylabel("Percentage (%)")
    ax5.tick_params(axis="x", rotation=45)

    # Plot 6: Top 10 PLZ by station count
    ax6 = axes[1, 2]
    if gdf_lstat3 is not None:
        top_plz = gdf_lstat3.nlargest(10, "Number")
        ax6.barh(top_plz["PLZ"].astype(str), top_plz["Number"], color="teal", edgecolor="black")
        ax6.set_title("Top 10 PLZ by Station Count")
        ax6.set_xlabel("Number of Stations")
        ax6.set_ylabel("PLZ")
        ax6.invert_yaxis()
    else:
        ax6.text(0.5, 0.5, "Processed data not available", ha="center", va="center", transform=ax6.transAxes)
        ax6.set_title("Top 10 PLZ by Station Count")

    plt.tight_layout()
    plt.savefig(os.path.join("assets", "data_quality_charging_stations.png"), dpi=300, bbox_inches="tight")
    print("\n✓ Saved: data_quality_charging_stations.png")
    plt.show()

    # ========== 2. RESIDENTS DATA ANALYSIS ==========
    print("\n" + "=" * 80)
    print("2. RESIDENTS DATA ANALYSIS")
    print("=" * 80)

    # Filter Berlin data
    df_residents_berlin = df_residents[(df_residents["plz"] > 10000) & (df_residents["plz"] < 14200)].copy()

    # Missing data analysis
    print("\n--- Missing Data in Residents ---")
    missing_resid = df_residents_berlin[["plz", "einwohner", "lat", "lon"]].isnull().sum()
    print(missing_resid)
    print(f"\nTotal records: {len(df_residents_berlin)}")

    # Statistical summary
    print("\n--- Statistical Summary: Population (Einwohner) ---")
    print(df_residents_berlin["einwohner"].describe())

    # Identify outliers using IQR method
    Q1_pop = df_residents_berlin["einwohner"].quantile(0.25)
    Q3_pop = df_residents_berlin["einwohner"].quantile(0.75)
    IQR_pop = Q3_pop - Q1_pop
    lower_bound_pop = Q1_pop - 1.5 * IQR_pop
    upper_bound_pop = Q3_pop + 1.5 * IQR_pop

    outliers_pop = df_residents_berlin[
        (df_residents_berlin["einwohner"] < lower_bound_pop) | (df_residents_berlin["einwohner"] > upper_bound_pop)
    ]
    print(f"\n--- Outliers in Population (IQR method) ---")
    print(f"Number of outliers: {len(outliers_pop)} ({len(outliers_pop)/len(df_residents_berlin)*100:.2f}%)")
    print(f"Outlier range: < {lower_bound_pop:.2f} or > {upper_bound_pop:.2f}")
    if len(outliers_pop) > 0:
        print("\nOutlier PLZ:")
        print(outliers_pop[["plz", "einwohner"]].to_string(index=False))

    # Create figure for residents analysis
    fig2, axes2 = plt.subplots(2, 3, figsize=(18, 12))
    fig2.suptitle("Residents Data Quality Analysis", fontsize=16, fontweight="bold")

    # Plot 1: Distribution of Population
    ax1_2 = axes2[0, 0]
    df_residents_berlin["einwohner"].hist(bins=40, ax=ax1_2, edgecolor="black", color="skyblue")
    ax1_2.set_title("Distribution of Population per PLZ")
    ax1_2.set_xlabel("Population (Einwohner)")
    ax1_2.set_ylabel("Frequency")
    ax1_2.axvline(df_residents_berlin["einwohner"].mean(), color="red", linestyle="--", label="Mean")
    ax1_2.axvline(df_residents_berlin["einwohner"].median(), color="green", linestyle="--", label="Median")
    ax1_2.legend()

    # Plot 2: Box plot for Population
    ax2_2 = axes2[0, 1]
    df_residents_berlin.boxplot(column="einwohner", ax=ax2_2)
    ax2_2.set_title("Box Plot: Population Outliers")
    ax2_2.set_ylabel("Population (Einwohner)")

    # Plot 3: Population Categories
    ax3_2 = axes2[0, 2]
    df_residents_berlin_copy = df_residents_berlin.copy()
    df_residents_berlin_copy["Pop_Category"] = pd.cut(
        df_residents_berlin_copy["einwohner"],
        bins=[0, 5000, 10000, 15000, 20000, float("inf")],
        labels=["Very Low (<5K)", "Low (5-10K)", "Medium (10-15K)", "High (15-20K)", "Very High (>20K)"],
    )
    pop_category_counts = df_residents_berlin_copy["Pop_Category"].value_counts()
    pop_category_counts.plot(kind="bar", ax=ax3_2, color="mediumseagreen", edgecolor="black")
    ax3_2.set_title("Distribution by Population Category")
    ax3_2.set_xlabel("Category")
    ax3_2.set_ylabel("Count")
    ax3_2.tick_params(axis="x", rotation=45)

    # Plot 4: Top 10 PLZ by Population
    ax4_2 = axes2[1, 0]
    if gdf_residents2 is not None:
        top_pop_plz = gdf_residents2.nlargest(10, "Einwohner")
        ax4_2.barh(top_pop_plz["PLZ"].astype(str), top_pop_plz["Einwohner"], color="mediumslateblue", edgecolor="black")
        ax4_2.set_title("Top 10 PLZ by Population")
        ax4_2.set_xlabel("Population")
        ax4_2.set_ylabel("PLZ")
        ax4_2.invert_yaxis()
    else:
        ax4_2.text(0.5, 0.5, "Processed data not available", ha="center", va="center", transform=ax4_2.transAxes)
        ax4_2.set_title("Top 10 PLZ by Population")

    # Plot 5: Missing data visualization
    ax5_2 = axes2[1, 1]
    missing_pct_resid = missing_resid / len(df_residents_berlin) * 100
    missing_pct_resid.plot(kind="bar", ax=ax5_2, color="lightcoral", edgecolor="black")
    ax5_2.set_title("Missing Data Percentage")
    ax5_2.set_ylabel("Percentage (%)")
    ax5_2.tick_params(axis="x", rotation=45)

    # Plot 6: Q-Q plot for normality check
    ax6_2 = axes2[1, 2]
    from scipy import stats

    stats.probplot(df_residents_berlin["einwohner"], dist="norm", plot=ax6_2)
    ax6_2.set_title("Q-Q Plot: Population Normality Check")
    ax6_2.grid(True)

    plt.tight_layout()
    plt.savefig(os.path.join("assets", "data_quality_residents.png"), dpi=300, bbox_inches="tight")
    print("\n✓ Saved: data_quality_residents.png")
    plt.show()

    # ========== 3. COMBINED ANALYSIS ==========
    if gdf_lstat3 is not None and gdf_residents2 is not None:
        print("\n" + "=" * 80)
        print("3. COMBINED ANALYSIS: STATIONS vs POPULATION")
        print("=" * 80)

        # Merge data
        combined = gdf_residents2.merge(gdf_lstat3[["PLZ", "Number"]], on="PLZ", how="left")
        combined["Number"] = combined["Number"].fillna(0)
        combined["Residents_per_Station"] = combined.apply(
            lambda row: row["Einwohner"] / row["Number"] if row["Number"] > 0 else np.nan, axis=1
        )

        # Create combined analysis figure
        fig3, axes3 = plt.subplots(2, 2, figsize=(15, 12))
        fig3.suptitle("Combined Analysis: Infrastructure vs Population", fontsize=16, fontweight="bold")

        # Plot 1: Scatter plot - Population vs Stations
        ax1_3 = axes3[0, 0]
        ax1_3.scatter(combined["Einwohner"], combined["Number"], alpha=0.6, s=100, c="blue", edgecolors="black")
        ax1_3.set_title("Population vs Charging Stations")
        ax1_3.set_xlabel("Population (Einwohner)")
        ax1_3.set_ylabel("Number of Stations")
        ax1_3.grid(True, alpha=0.3)

        corr = combined[["Einwohner", "Number"]].corr().iloc[0, 1]
        ax1_3.text(
            0.05,
            0.95,
            f"Correlation: {corr:.3f}",
            transform=ax1_3.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
        )

        print(f"\n--- Correlation Analysis ---")
        print(f"Correlation between Population and Stations: {corr:.3f}")

        # Plot 2: Distribution of Residents per Station
        ax2_3 = axes3[0, 1]
        residents_per_station_clean = combined["Residents_per_Station"].dropna()
        if len(residents_per_station_clean) > 0:
            residents_per_station_clean.hist(bins=30, ax=ax2_3, edgecolor="black", color="orange")
            ax2_3.set_title("Distribution: Residents per Station")
            ax2_3.set_xlabel("Residents per Station")
            ax2_3.set_ylabel("Frequency")
            ax2_3.axvline(residents_per_station_clean.mean(), color="red", linestyle="--", label="Mean")
            ax2_3.axvline(residents_per_station_clean.median(), color="green", linestyle="--", label="Median")
            ax2_3.legend()

            print(f"\n--- Residents per Station Statistics ---")
            print(residents_per_station_clean.describe())

        # Plot 3: Heatmap - Correlation matrix
        ax3_3 = axes3[1, 0]
        corr_matrix = combined[["Einwohner", "Number"]].corr()
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".3f",
            cmap="coolwarm",
            square=True,
            ax=ax3_3,
            cbar_kws={"label": "Correlation"},
        )
        ax3_3.set_title("Correlation Heatmap")

        # Plot 4: PLZ without stations
        ax4_3 = axes3[1, 1]
        plz_no_stations = combined[combined["Number"] == 0]
        print(f"\n--- PLZ without Charging Stations ---")
        print(f"Number of PLZ without stations: {len(plz_no_stations)}")
        if len(plz_no_stations) > 0:
            print("\nPLZ without stations:")
            print(plz_no_stations[["PLZ", "Einwohner"]].to_string(index=False))

            # Bar plot of population in PLZ without stations
            if len(plz_no_stations) <= 20:
                ax4_3.barh(
                    plz_no_stations["PLZ"].astype(str), plz_no_stations["Einwohner"], color="crimson", edgecolor="black"
                )
                ax4_3.set_title("Population in PLZ without Stations")
                ax4_3.set_xlabel("Population")
                ax4_3.set_ylabel("PLZ")
                ax4_3.invert_yaxis()
            else:
                ax4_3.text(
                    0.5,
                    0.5,
                    f"{len(plz_no_stations)} PLZ\nwithout stations",
                    ha="center",
                    va="center",
                    transform=ax4_3.transAxes,
                    fontsize=14,
                )
                ax4_3.set_title("PLZ without Stations")

        plt.tight_layout()
        plt.savefig(os.path.join("assets", "data_quality_combined.png"), dpi=300, bbox_inches="tight")
        print("\n✓ Saved: data_quality_combined.png")
        plt.show()

    # ========== SUMMARY ==========
    print("\n" + "=" * 80)
    print("SUMMARY: KEY FINDINGS")
    print("=" * 80)
    print("\n✓ Charging Stations:")
    print(f"  - Total Berlin stations: {len(df_lstat_berlin)}")
    print(
        f"  - Power capacity range: {df_lstat_berlin['KW_numeric'].min():.2f} - {df_lstat_berlin['KW_numeric'].max():.2f} kW"
    )
    print(f"  - Power capacity outliers: {len(outliers_kw)} ({len(outliers_kw)/len(df_lstat_berlin)*100:.2f}%)")

    print("\n✓ Residents:")
    print(f"  - Total Berlin PLZ: {len(df_residents_berlin)}")
    print(
        f"  - Population range: {df_residents_berlin['einwohner'].min():,} - {df_residents_berlin['einwohner'].max():,}"
    )
    print(f"  - Population outliers: {len(outliers_pop)} ({len(outliers_pop)/len(df_residents_berlin)*100:.2f}%)")

    if gdf_lstat3 is not None and gdf_residents2 is not None:
        print("\n✓ Infrastructure Coverage:")
        print(f"  - Correlation (Population vs Stations): {corr:.3f}")
        print(f"  - PLZ without stations: {len(plz_no_stations)}")
        print(f"  - Average residents per station: {residents_per_station_clean.mean():.1f}")

    print("\n" + "=" * 80 + "\n")
