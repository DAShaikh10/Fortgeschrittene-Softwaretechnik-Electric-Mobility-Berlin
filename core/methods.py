import folium
import streamlit as st
import geopandas as gpd
import pandas as pd
import core.helper_tools as ht

from streamlit_folium import folium_static
from branca.colormap import LinearColormap


def sort_by_plz_add_geometry(dfr, dfg, pdict):
    dframe = dfr.copy()
    df_geo = dfg.copy()

    sorted_df = dframe.sort_values(by="PLZ").reset_index(drop=True).sort_index()

    sorted_df2 = sorted_df.merge(df_geo, on=pdict["geocode"], how="left")
    sorted_df3 = sorted_df2.dropna(subset=["geometry"])

    sorted_df3["geometry"] = gpd.GeoSeries.from_wkt(sorted_df3["geometry"])
    ret = gpd.GeoDataFrame(sorted_df3, geometry="geometry")

    return ret


# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocessing dataframe from Ladesaeulenregister.csv"""
    dframe = dfr.copy()
    df_geo = dfg.copy()

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
        inplace=True,
    )

    # Convert to string
    dframe2["Breitengrad"] = dframe2["Breitengrad"].astype(str)
    dframe2["Längengrad"] = dframe2["Längengrad"].astype(str)

    # Now replace the commas with periods
    dframe2["Breitengrad"] = dframe2["Breitengrad"].str.replace(",", ".")
    dframe2["Längengrad"] = dframe2["Längengrad"].str.replace(",", ".")

    dframe3 = dframe2[(dframe2["Bundesland"] == "Berlin") & (dframe2["PLZ"] > 10115) & (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)

    return ret


# -----------------------------------------------------------------------------
@ht.timer
def count_plz_occurrences(df_lstat2):
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby("PLZ").agg(Number=("PLZ", "count"), geometry=("geometry", "first")).reset_index()

    return result_df


# -----------------------------------------------------------------------------
@ht.timer
def count_plz_by_power_category(df_lstat2):
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
    df['KW_numeric'] = pd.to_numeric(df['KW'], errors='coerce')
    
    # Remove rows with invalid KW values
    df = df.dropna(subset=['KW_numeric'])
    
    # Define power categories
    def categorize_power(kw):
        if kw < 11:
            return 'Slow'
        elif kw < 22:
            return 'Normal'
        elif kw < 50:
            return 'Fast'
        elif kw < 150:
            return 'Rapid'
        else:
            return 'Ultra-rapid'
    
    df['Power_Category'] = df['KW_numeric'].apply(categorize_power)
    
    # Group by PLZ and power category
    result_dict = {}
    
    # Total count (same as count_plz_occurrences)
    result_dict['Total'] = df.groupby("PLZ").agg(
        Number=("PLZ", "count"), 
        geometry=("geometry", "first")
    ).reset_index()
    
    # Count by category
    categories = ['Slow', 'Normal', 'Fast', 'Rapid', 'Ultra-rapid']
    for category in categories:
        df_category = df[df['Power_Category'] == category]
        if len(df_category) > 0:
            result_dict[category] = df_category.groupby("PLZ").agg(
                Number=("PLZ", "count"), 
                geometry=("geometry", "first")
            ).reset_index()
        else:
            # Empty dataframe with correct structure
            result_dict[category] = gpd.GeoDataFrame(
                columns=['PLZ', 'Number', 'geometry']
            )
    
    return result_dict


# -----------------------------------------------------------------------------
# @ht.timer
# def preprop_geb(dfr, pdict):
#     """Preprocessing dataframe from gebaeude.csv"""
#     dframe      = dfr.copy()

#     dframe2     = dframe .loc[:,['lag', 'bezbaw', 'geometry']]
#     dframe2.rename(columns      = {"bezbaw":"Gebaeudeart", "lag": "PLZ"}, inplace = True)


#     # Now, let's filter the DataFrame
#     dframe3 = dframe2[
#         dframe2['PLZ'].notna() &  # Remove NaN values
#         ~dframe2['PLZ'].astype(str).str.contains(',') &  # Remove entries with commas
#         (dframe2['PLZ'].astype(str).str.len() <= 5)  # Keep entries with 5 or fewer characters
#         ]

#     # Convert PLZ to numeric, coercing errors to NaN
#     dframe3['PLZ_numeric'] = pd.to_numeric(dframe3['PLZ'], errors='coerce')

#     # Filter for PLZ between 10000 and 14200
#     filtered_df = dframe3[
#         (dframe3['PLZ_numeric'] >= 10000) &
#         (dframe3['PLZ_numeric'] <= 14200)
#     ]

#     # Drop the temporary numeric column
#     filtered_df2 = filtered_df.drop('PLZ_numeric', axis=1)

#     filtered_df3 = filtered_df2[filtered_df2['Gebaeudeart'].isin(['Freistehendes Einzelgebäude', 'Doppelhaushälfte'])]

#     filtered_df4 = (filtered_df3\
#                  .assign(PLZ=lambda x: pd.to_numeric(x['PLZ'], errors='coerce'))[['PLZ', 'Gebaeudeart', 'geometry']]
#                  .sort_values(by='PLZ')
#                  .reset_index(drop=True)
#                  )

#     ret                     = filtered_df4.dropna(subset=['geometry'])

#     return ret


# -----------------------------------------------------------------------------
@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe = dfr.copy()
    df_geo = dfg.copy()

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

    # Convert to string
    dframe2["Breitengrad"] = dframe2["Breitengrad"].astype(str)
    dframe2["Längengrad"] = dframe2["Längengrad"].astype(str)

    # Now replace the commas with periods
    dframe2["Breitengrad"] = dframe2["Breitengrad"].str.replace(",", ".")
    dframe2["Längengrad"] = dframe2["Längengrad"].str.replace(",", ".")

    dframe3 = dframe2[(dframe2["PLZ"] > 10000) & (dframe2["PLZ"] < 14200)]

    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)

    return ret


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_Charging_resid(dfr1, dfr2):
    """Makes Streamlit App with Heatmap of Electric Charging Stations and Residents"""

    dframe1 = dfr1.copy()
    dframe2 = dfr2.copy()

    # Streamlit app
    st.title("Heatmaps: Electric Charging Stations and Residents")

    # Create a radio button for layer selection
    # layer_selection = st.radio("Select Layer", ("Number of Residents per PLZ (Postal code)", "Number of Charging Stations per PLZ (Postal code)"))

    layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations"))

    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":

        # Create a color map for Residents
        color_map = LinearColormap(
            colors=["yellow", "red"],
            vmin=dframe2["Einwohner"].min(),
            vmax=dframe2["Einwohner"].max(),
        )

        # Add polygons to the map for Residents
        for idx, row in dframe2.iterrows():
            folium.GeoJson(
                row["geometry"],
                style_function=lambda x, color=color_map(row["Einwohner"]): {
                    "fillColor": color,
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.7,
                },
                tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}",
            ).add_to(m)

        # Display the dataframe for Residents
        # st.subheader('Residents Data')
        # st.dataframe(gdf_residents2)

    else:
        # Create a color map for Numbers

        color_map = LinearColormap(
            colors=["yellow", "red"],
            vmin=dframe1["Number"].min(),
            vmax=dframe1["Number"].max(),
        )

        # Add polygons to the map for Numbers
        for idx, row in dframe1.iterrows():
            folium.GeoJson(
                row["geometry"],
                style_function=lambda x, color=color_map(row["Number"]): {
                    "fillColor": color,
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.7,
                },
                tooltip=f"PLZ: {row['PLZ']}, Number: {row['Number']}",
            ).add_to(m)

        # Display the dataframe for Numbers
        # st.subheader('Numbers Data')
        # st.dataframe(gdf_lstat3)

    # Add color map to the map
    color_map.add_to(m)

    folium_static(m, width=800, height=600)


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_with_power_categories(power_dict, dfr_residents):
    """
    Makes Streamlit App with separate layers for each power category (kW).
    
    Args:
        power_dict: Dictionary with DataFrames for each power category
        dfr_residents: Residents GeoDataFrame
    """
    dframe_residents = dfr_residents.copy()
    
    # Streamlit app
    st.title("Heatmaps: Electric Charging Stations by Power Rating and Residents")
    
    st.markdown("""
    This visualization shows charging station distribution categorized by power rating:
    - **Slow (<11 kW):** Typically home/overnight charging
    - **Normal (11-22 kW):** Public AC charging, 2-4 hours for full charge
    - **Fast (22-50 kW):** Public AC/DC charging, 1-2 hours
    - **Rapid (50-150 kW):** DC fast charging, 20-40 minutes
    - **Ultra-rapid (≥150 kW):** Ultra-fast DC charging, 15-20 minutes
    """)
    
    # Create layer selection options
    layer_options = ["Residents", "All Charging Stations"] + \
                    ["Slow Charging (<11 kW)", "Normal Charging (11-22 kW)", 
                     "Fast Charging (22-50 kW)", "Rapid Charging (50-150 kW)", 
                     "Ultra-rapid Charging (≥150 kW)"]
    
    layer_selection = st.radio("Select Layer", layer_options)
    
    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)
    
    # Mapping between selection and power_dict keys
    layer_mapping = {
        "All Charging Stations": "Total",
        "Slow Charging (<11 kW)": "Slow",
        "Normal Charging (11-22 kW)": "Normal",
        "Fast Charging (22-50 kW)": "Fast",
        "Rapid Charging (50-150 kW)": "Rapid",
        "Ultra-rapid Charging (≥150 kW)": "Ultra-rapid"
    }
    
    if layer_selection == "Residents":
        # Create a color map for Residents
        if len(dframe_residents) > 0 and dframe_residents["Einwohner"].max() > dframe_residents["Einwohner"].min():
            color_map = LinearColormap(
                colors=["yellow", "red"],
                vmin=dframe_residents["Einwohner"].min(),
                vmax=dframe_residents["Einwohner"].max(),
            )
            
            # Add polygons to the map for Residents
            for idx, row in dframe_residents.iterrows():
                folium.GeoJson(
                    row["geometry"],
                    style_function=lambda x, color=color_map(row["Einwohner"]): {
                        "fillColor": color,
                        "color": "black",
                        "weight": 1,
                        "fillOpacity": 0.7,
                    },
                    tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}",
                ).add_to(m)
            
            color_map.add_to(m)
        else:
            st.warning("No resident data available for visualization")
    
    else:
        # Get the appropriate dataframe based on selection
        category_key = layer_mapping.get(layer_selection, "Total")
        dframe_stations = power_dict.get(category_key)
        
        if dframe_stations is not None and len(dframe_stations) > 0:
            # Check if there's variation in the data
            if dframe_stations["Number"].max() > dframe_stations["Number"].min():
                # Create a color map for charging stations
                color_map = LinearColormap(
                    colors=["yellow", "red"],
                    vmin=dframe_stations["Number"].min(),
                    vmax=dframe_stations["Number"].max(),
                )
                
                # Add polygons to the map
                for idx, row in dframe_stations.iterrows():
                    folium.GeoJson(
                        row["geometry"],
                        style_function=lambda x, color=color_map(row["Number"]): {
                            "fillColor": color,
                            "color": "black",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=f"PLZ: {row['PLZ']}, Stations: {row['Number']}",
                    ).add_to(m)
                
                color_map.add_to(m)
                
                # Display statistics
                st.sidebar.markdown(f"### {layer_selection} Statistics")
                st.sidebar.write(f"Total Stations: {dframe_stations['Number'].sum()}")
                st.sidebar.write(f"Areas Covered: {len(dframe_stations)}")
                st.sidebar.write(f"Average per PLZ: {dframe_stations['Number'].mean():.1f}")
                st.sidebar.write(f"Max in one PLZ: {dframe_stations['Number'].max()}")
            else:
                st.info(f"All areas have the same number of stations ({dframe_stations['Number'].iloc[0]}) in this category")
                # Still show the data with a single color
                for idx, row in dframe_stations.iterrows():
                    folium.GeoJson(
                        row["geometry"],
                        style_function=lambda x: {
                            "fillColor": "orange",
                            "color": "black",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=f"PLZ: {row['PLZ']}, Stations: {row['Number']}",
                    ).add_to(m)
        else:
            st.warning(f"No charging stations found in the '{layer_selection}' category for Berlin")
            st.info("This may indicate that this power category is not commonly deployed in Berlin's charging infrastructure")
    
    folium_static(m, width=800, height=600)


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_with_enhanced_features(power_dict, dfr_residents, df_lstat_full):
    """
    Makes Streamlit App with power categories, search by zip code, and dropdown filtering.
    
    Args:
        power_dict: Dictionary with DataFrames for each power category
        dfr_residents: Residents GeoDataFrame
        df_lstat_full: Full preprocessed charging station DataFrame with all details
    """
    dframe_residents = dfr_residents.copy()
    df_stations_full = df_lstat_full.copy()
    
    # Streamlit app
    st.title("EVision Berlin")
    
    # Get all available PLZ from both datasets
    all_plz_stations = set(power_dict['Total']['PLZ'].tolist()) if len(power_dict['Total']) > 0 else set()
    all_plz_residents = set(dframe_residents['PLZ'].tolist()) if len(dframe_residents) > 0 else set()
    all_plz = sorted(list(all_plz_stations.union(all_plz_residents)))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Search by ZIP Code**")
        search_plz = st.text_input(
            "Enter ZIP Code (PLZ):",
            placeholder="e.g., 10115",
            help="Enter a Berlin postal code to highlight it on the map",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**Filter by Power Category**")
        power_categories = {
            "All Charging Stations": "Total",
            "Slow (<11 kW)": "Slow",
            "Normal (11-22 kW)": "Normal",
            "Fast (22-50 kW)": "Fast",
            "Rapid (50-150 kW)": "Rapid",
            "Ultra-rapid (≥150 kW)": "Ultra-rapid"
        }
        
        selected_power = st.selectbox(
            "Select Power Category:",
            options=list(power_categories.keys()),
            help="Filter charging stations by their power rating",
            label_visibility="collapsed"
        )
    
    # Validate and process search
    highlighted_plz = None
    if search_plz:
        try:
            plz_int = int(search_plz)
            if plz_int in all_plz:
                highlighted_plz = plz_int
                st.success(f"Found PLZ: {plz_int}")
            else:
                st.error(f"PLZ {plz_int} not found in dataset")
        except ValueError:
            st.error("Please enter a valid numeric ZIP code")
    
    # Layer selection on main screen
    st.markdown("**Visualization Layer**")
    layer_selection = st.radio(
        "Select Data Layer:",
        ("Population Density", "Charging Stations"),
        horizontal=True,
        help="Choose between viewing population or charging station distribution",
        label_visibility="collapsed"
    )
    
    # Sidebar for statistics
    st.sidebar.header("Statistics")
    
    # Create the map
    if highlighted_plz:
        # Try to find coordinates for the highlighted PLZ
        plz_coords = None
        if highlighted_plz in dframe_residents['PLZ'].values:
            plz_row = dframe_residents[dframe_residents['PLZ'] == highlighted_plz].iloc[0]
            # Get centroid of geometry
            centroid = plz_row['geometry'].centroid
            plz_coords = [centroid.y, centroid.x]
        
        if plz_coords:
            m = folium.Map(location=plz_coords, zoom_start=13)
        else:
            m = folium.Map(location=[52.52, 13.40], zoom_start=10)
    else:
        m = folium.Map(location=[52.52, 13.40], zoom_start=10)
    
    # Render based on layer selection
    if layer_selection == "Population Density":
        # Render population heatmap
        if len(dframe_residents) > 0 and dframe_residents["Einwohner"].max() > dframe_residents["Einwohner"].min():
            color_map = LinearColormap(
                colors=["yellow", "orange", "red"],
                vmin=dframe_residents["Einwohner"].min(),
                vmax=dframe_residents["Einwohner"].max(),
                caption="Number of Residents"
            )
            
            for idx, row in dframe_residents.iterrows():
                is_highlighted = (highlighted_plz and row['PLZ'] == highlighted_plz)
                
                folium.GeoJson(
                    row["geometry"],
                    style_function=lambda x, color=color_map(row["Einwohner"]), highlight=is_highlighted: {
                        "fillColor": color,
                        "color": "blue" if highlight else "black",
                        "weight": 3 if highlight else 1,
                        "fillOpacity": 0.7,
                    },
                    tooltip=f"PLZ: {row['PLZ']}<br>Residents: {row['Einwohner']:,}",
                ).add_to(m)
            
            color_map.add_to(m)
            
            # Display statistics in sidebar
            st.sidebar.markdown("### Population Statistics")
            st.sidebar.metric("Total Population", f"{dframe_residents['Einwohner'].sum():,}")
            st.sidebar.metric("Number of Areas", len(dframe_residents))
            st.sidebar.metric("Avg per PLZ", f"{dframe_residents['Einwohner'].mean():.0f}")
            
            if highlighted_plz and highlighted_plz in dframe_residents['PLZ'].values:
                plz_data = dframe_residents[dframe_residents['PLZ'] == highlighted_plz].iloc[0]
                st.sidebar.markdown("---")
                st.sidebar.markdown(f"### PLZ {highlighted_plz}")
                st.sidebar.metric("Residents", f"{plz_data['Einwohner']:,}")
        else:
            st.warning("No population data available for visualization")
    
    else:  # Charging Stations
        # Get the selected power category data
        category_key = power_categories[selected_power]
        dframe_stations = power_dict.get(category_key)
        
        if dframe_stations is not None and len(dframe_stations) > 0:
            if dframe_stations["Number"].max() > dframe_stations["Number"].min():
                color_map = LinearColormap(
                    colors=["yellow", "orange", "red"],
                    vmin=dframe_stations["Number"].min(),
                    vmax=dframe_stations["Number"].max(),
                    caption=f"Number of {selected_power} Stations"
                )
                
                for idx, row in dframe_stations.iterrows():
                    is_highlighted = (highlighted_plz and row['PLZ'] == highlighted_plz)
                    
                    folium.GeoJson(
                        row["geometry"],
                        style_function=lambda x, color=color_map(row["Number"]), highlight=is_highlighted: {
                            "fillColor": color,
                            "color": "blue" if highlight else "black",
                            "weight": 3 if highlight else 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=f"PLZ: {row['PLZ']}<br>{selected_power}: {row['Number']} stations",
                    ).add_to(m)
                
                color_map.add_to(m)
                
                # Display statistics in sidebar
                st.sidebar.markdown(f"### {selected_power}")
                st.sidebar.metric("Total Stations", int(dframe_stations['Number'].sum()))
                st.sidebar.metric("Areas Covered", len(dframe_stations))
                st.sidebar.metric("Avg per PLZ", f"{dframe_stations['Number'].mean():.1f}")
                st.sidebar.metric("Max in one PLZ", int(dframe_stations['Number'].max()))
                
                if highlighted_plz and highlighted_plz in dframe_stations['PLZ'].values:
                    plz_data = dframe_stations[dframe_stations['PLZ'] == highlighted_plz].iloc[0]
                    st.sidebar.markdown("---")
                    st.sidebar.markdown(f"### PLZ {highlighted_plz}")
                    st.sidebar.metric(f"{selected_power}", f"{int(plz_data['Number'])} stations")
            else:
                # All areas have same number - show with single color
                st.info(f"All areas have {int(dframe_stations['Number'].iloc[0])} stations in this category")
                
                for idx, row in dframe_stations.iterrows():
                    is_highlighted = (highlighted_plz and row['PLZ'] == highlighted_plz)
                    
                    folium.GeoJson(
                        row["geometry"],
                        style_function=lambda x, highlight=is_highlighted: {
                            "fillColor": "orange",
                            "color": "blue" if highlight else "black",
                            "weight": 3 if highlight else 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=f"PLZ: {row['PLZ']}<br>Stations: {row['Number']}",
                    ).add_to(m)
        else:
            st.warning(f"No charging stations found in the '{selected_power}' category")
            st.info("This power category may not be commonly deployed in Berlin's infrastructure")
    
    # Add highlighted marker if PLZ was searched and found
    if highlighted_plz:
        if highlighted_plz in dframe_residents['PLZ'].values:
            plz_row = dframe_residents[dframe_residents['PLZ'] == highlighted_plz].iloc[0]
            centroid = plz_row['geometry'].centroid
            
            folium.Marker(
                location=[centroid.y, centroid.x],
                popup=f"<b>PLZ: {highlighted_plz}</b>",
                icon=folium.Icon(color='blue', icon='info-sign'),
                tooltip=f"Searched: PLZ {highlighted_plz}"
            ).add_to(m)
    
    # Display the map
    folium_static(m, width=800, height=600)
