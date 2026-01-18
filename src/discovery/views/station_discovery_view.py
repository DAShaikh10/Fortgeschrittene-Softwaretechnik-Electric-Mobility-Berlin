"""
Station Discovery View - Discovery Bounded Context.

This view handles visualization of charging stations and postal code areas,
following DDD principles by keeping UI concerns within the Discovery context.
"""

import json
import folium
import streamlit
import pandas as pd

from src.shared.infrastructure import get_logger
from src.shared.domain.value_objects import PostalCode
from src.shared.application.services import (
    ChargingStationService,
    GeoLocationService,
    PostalCodeResidentService,
)

logger = get_logger(__name__)


class StationDiscoveryView:
    """
    View component for Charging Station Discovery visualization.

    Responsibilities:
    - Render charging station map markers
    - Display postal code boundaries
    - Visualize resident distribution
    - Handle map interactions for station discovery
    """

    def __init__(
        self,
        charging_station_service: ChargingStationService,
        geolocation_service: GeoLocationService,
        postal_code_residents_service: PostalCodeResidentService,
    ):
        """
        Initialize Station Discovery View.

        Args:
            charging_station_service: Service for charging station operations.
            geolocation_service: Service for geolocation data.
            postal_code_residents_service: Service for postal code resident data.
        """
        self.charging_station_service = charging_station_service
        self.geolocation_service = geolocation_service
        self.postal_code_residents_service = postal_code_residents_service

    def render_charging_stations_layer(self, folium_map: folium.Map, selected_postal_code: str):
        """
        Render charging station markers and postal code boundary on the map.

        Args:
            folium_map: The Folium map object to add markers to.
            selected_postal_code: The postal code to display stations for.
        """
        try:
            if selected_postal_code and selected_postal_code not in ("", "All areas"):
                self._render_specific_area_stations(folium_map, selected_postal_code)
            else:
                self._render_all_areas_by_station_count(folium_map)

        except Exception as e:
            logger.error("Error loading charging stations: %s", e, exc_info=True)
            streamlit.error(f"Error loading charging stations: {e}")

    def _render_specific_area_stations(self, folium_map: folium.Map, selected_postal_code: str):
        """Render specific postal code with its charging stations."""
        logger.info("=== Rendering charging stations for PLZ: %s ===", selected_postal_code)
        postal_code_obj = PostalCode(selected_postal_code)

        # Render boundary
        plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

        if plz_geometry is not None and plz_geometry.boundary is not None:
            try:
                boundary_geojson = json.loads(plz_geometry.boundary.to_json())
                folium.GeoJson(
                    boundary_geojson,
                    name=f"Postal Code {selected_postal_code}",
                    style_function=lambda x: {
                        "fillColor": "#3186cc",
                        "color": "#0066cc",
                        "weight": 2,
                        "fillOpacity": 0.5,
                    },
                    tooltip=f"Postal Code: {selected_postal_code}",
                ).add_to(folium_map)
            except Exception as boundary_error:
                logger.error("Error rendering boundary: %s", boundary_error, exc_info=True)
                streamlit.error(f"Error rendering postal code boundary: {boundary_error}")
        else:
            streamlit.warning(f"No boundary data available for postal code {selected_postal_code}")

        # Render stations
        stations = self.charging_station_service.find_stations_by_postal_code(postal_code_obj)
        logger.info("Found %d charging stations", len(stations))

        for station in stations:
            # Create custom icon with electric charging symbol
            icon_html = """
            <div style="
                background-color: #1bbc9b;
                border: 3px solid #148f77;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            ">⚡</div>
            """

            popup_content = f"""
            <div style="font-family: Arial; min-width: 150px;">
                <b>⚡ Charging Station</b><br>
                <hr style="margin: 5px 0;">
                📍 <b>PLZ:</b> {station.postal_code.value}<br>
                🔋 <b>Power:</b> {station.power_capacity.kilowatts} kW
            </div>
            """

            folium.Marker(
                location=[station.latitude, station.longitude],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=f"⚡ {station.power_capacity.kilowatts} kW",
                icon=folium.DivIcon(html=icon_html),
            ).add_to(folium_map)

    def _render_all_areas_by_station_count(self, folium_map: folium.Map):  # pylint: disable=too-many-locals
        """Render all postal codes colored by station count."""
        logger.info("=== Rendering all postal codes by charging station count ===")

        postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

        station_data = []
        for postal_code in postal_codes:
            postal_code_area = self.charging_station_service.search_by_postal_code(postal_code)
            station_count = postal_code_area.station_count if postal_code_area else 0

            resident_data = self.postal_code_residents_service.get_resident_data(postal_code)
            population = resident_data.get_population() if resident_data else 0

            station_data.append(
                {"postal_code": postal_code.value, "station_count": station_count, "population": population}
            )

        if not station_data:
            streamlit.warning("No charging station data available for visualization.")
            return

        stations_df = pd.DataFrame(station_data)
        max_stations = stations_df["station_count"].max()
        min_stations = stations_df["station_count"].min()

        areas_rendered = 0

        for _, row in stations_df.iterrows():
            try:
                plz = row["postal_code"]
                station_count = row["station_count"]
                population = row["population"]

                postal_code_obj = PostalCode(plz)
                plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                if plz_geometry is not None and plz_geometry.boundary is not None:
                    # Calculate color based on station count (green gradient)
                    if max_stations > min_stations:
                        normalized = (station_count - min_stations) / (max_stations - min_stations)
                    else:
                        normalized = 0.5

                    # Color gradient from light green to dark green
                    r = int(200 - (200 - 27) * normalized)
                    g = int(230 - (230 - 94) * normalized)
                    b = int(201 - (201 - 32) * normalized)
                    fill_color = f"#{r:02x}{g:02x}{b:02x}"

                    boundary_geojson = json.loads(plz_geometry.boundary.to_json())

                    folium.GeoJson(
                        boundary_geojson,
                        name=f"PLZ {plz}",
                        style_function=lambda x, color=fill_color: {
                            "fillColor": color,
                            "color": "#666666",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=(
                            f"Postal Code: {plz}<br>👥 Population: {population:,}<br>⚡ Stations: {station_count}"
                        ),
                    ).add_to(folium_map)
                    areas_rendered += 1
            except Exception as e:
                logger.warning("Could not render postal code %s: %s", plz, e)

        logger.info("✓ Rendered %d postal code areas by station count", areas_rendered)

    def render_residents_layer(self, folium_map: folium.Map, selected_postal_code: str):
        """
        Render population density visualization on the map.

        Args:
            folium_map: The Folium map object to add layer to.
            selected_postal_code: The selected postal code to display.
        """
        try:
            if selected_postal_code and selected_postal_code not in ("", "All areas"):
                self._render_specific_area_residents(folium_map, selected_postal_code)
            else:
                self._render_all_areas_by_population(folium_map)

        except Exception as e:
            logger.error("Error loading residents layer: %s", e, exc_info=True)
            streamlit.error(f"Error loading residents layer: {e}")

    def _render_specific_area_residents(self, folium_map: folium.Map, selected_postal_code: str):
        """Render specific postal code with population data."""
        logger.info("=== Rendering residents layer for PLZ: %s ===", selected_postal_code)
        postal_code_obj = PostalCode(selected_postal_code)

        plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)
        resident_data = self.postal_code_residents_service.get_resident_data(postal_code_obj)

        if plz_geometry is not None and plz_geometry.boundary is not None and resident_data:
            try:
                population = resident_data.get_population()
                boundary_geojson = json.loads(plz_geometry.boundary.to_json())

                folium.GeoJson(
                    boundary_geojson,
                    name=f"Postal Code {selected_postal_code}",
                    style_function=lambda x: {
                        "fillColor": "#ff9800",
                        "color": "#f57c00",
                        "weight": 2,
                        "fillOpacity": 0.5,
                    },
                    tooltip=f"Postal Code: {selected_postal_code}<br>👥 Population: {population:,}",
                ).add_to(folium_map)

                logger.info("✓ Postal code boundary with population data added successfully!")
            except Exception as boundary_error:
                logger.error("Error rendering residents boundary: %s", boundary_error, exc_info=True)
                streamlit.error(f"Error rendering postal code boundary: {boundary_error}")
        else:
            streamlit.warning(f"No resident data available for postal code {selected_postal_code}")

    def _render_all_areas_by_population(self, folium_map: folium.Map):  # pylint: disable=too-many-locals
        """Render all postal codes colored by population."""
        logger.info("=== Rendering all postal codes by population ===")

        postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

        population_data = []
        for postal_code in postal_codes:
            resident_data = self.postal_code_residents_service.get_resident_data(postal_code)
            if resident_data:
                population_data.append({"postal_code": postal_code.value, "population": resident_data.get_population()})

        if not population_data:
            streamlit.warning("No population data available for visualization.")
            return

        pop_df = pd.DataFrame(population_data)
        max_population = pop_df["population"].max()
        min_population = pop_df["population"].min()

        areas_rendered = 0

        for _, row in pop_df.iterrows():
            try:
                plz = row["postal_code"]
                population = row["population"]

                postal_code_obj = PostalCode(plz)
                plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                if plz_geometry is not None and plz_geometry.boundary is not None:
                    postal_code_area = self.charging_station_service.search_by_postal_code(postal_code_obj)
                    station_count = postal_code_area.station_count if postal_code_area else 0

                    # Calculate color based on population (orange gradient)
                    normalized = (
                        (population - min_population) / (max_population - min_population)
                        if max_population > min_population
                        else 0.5
                    )

                    # Color gradient from light orange to dark orange
                    r = int(255 - (255 - 230) * normalized)
                    g = int(224 - (224 - 81) * normalized)
                    b = int(178 - (178 - 0) * normalized)
                    fill_color = f"#{r:02x}{g:02x}{b:02x}"

                    boundary_geojson = json.loads(plz_geometry.boundary.to_json())

                    folium.GeoJson(
                        boundary_geojson,
                        name=f"PLZ {plz}",
                        style_function=lambda x, color=fill_color: {
                            "fillColor": color,
                            "color": "#666666",
                            "weight": 1,
                            "fillOpacity": 0.7,
                        },
                        tooltip=(
                            f"Postal Code: {plz}<br>👥 Population: {population:,}<br>⚡ Stations: {station_count}"
                        ),
                    ).add_to(folium_map)
                    areas_rendered += 1
            except Exception as e:
                logger.warning("Could not render postal code %s: %s", plz, e)

        logger.info("✓ Rendered %d postal code areas by population", areas_rendered)
