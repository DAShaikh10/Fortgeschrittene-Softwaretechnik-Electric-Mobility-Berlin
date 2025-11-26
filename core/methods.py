import os
import folium
import pandas as pd
import streamlit as st
import geopandas as gpd
import pandas as pd
import core.helper_tools as ht

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
