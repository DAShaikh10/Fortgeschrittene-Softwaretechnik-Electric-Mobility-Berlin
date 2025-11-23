import folium
import streamlit as st
import geopandas as gpd
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
