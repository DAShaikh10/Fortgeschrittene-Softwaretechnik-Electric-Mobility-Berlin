"""
Streamlit Application for EVision Berlin.
"""

import json

import folium
import streamlit
import pandas as pd

from streamlit_folium import folium_static

from docs import ABOUT_SECTION

from src.shared.infrastructure.logging_config import get_logger
from src.shared.domain.events import IDomainEventPublisher
from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.application.services import (
    ChargingStationService,
    GeoLocationService,
    PostalCodeResidentService,
    PowerCapacityService,
)
from src.demand.application.services import DemandAnalysisService

logger = get_logger(__name__)


class StreamlitApp:
    """
    Streamlit application for EVision Berlin infrastructure analysis.

    This class provides the UI layer using Streamlit, integrating with
    DDD / TDD application services from Charging Station Discovery and New Charging Station Demand Analysis contexts.
    """

    def __init__(
        self,
        postal_code_residents_service: PostalCodeResidentService,
        charging_station_service: ChargingStationService,
        geolocation_service: GeoLocationService,
        demand_analysis_service: DemandAnalysisService,
        power_capacity_service: PowerCapacityService,
        event_bus: IDomainEventPublisher,
        valid_plzs: list[int],
    ):
        """
        Initialize EVision Berlin Streamlit application.

        Args:
            postal_code_residents_service (PostalCodeResidentService): Service for postal code residents.
            charging_station_service (ChargingStationService): Service for charging stations.
            geolocation_service (GeoLocationService): Service for geolocation data.
            demand_analysis_service (DemandAnalysisService): Service for demand analysis.
            power_capacity_service (PowerCapacityService): Service for power capacity analysis.
            event_bus (IDomainEventPublisher): Domain event bus interface.
            valid_plzs (list[int]): List of valid Berlin postal codes for validation.
        """

        self.postal_code_residents_service = postal_code_residents_service
        self.charging_station_service = charging_station_service
        self.geolocation_service = geolocation_service
        self.demand_analysis_service = demand_analysis_service
        self.power_capacity_service = power_capacity_service
        self.event_bus = event_bus
        self.valid_plzs = valid_plzs

    def _validate_plz_input(self, plz_input: str) -> tuple[bool, str]:
        """
        Validates a postal code input string against Berlin requirements.

        Clean Code Principle: Single Responsibility (Validation Logic).

        Args:
            plz_input (str): The raw input string from the user.

        Returns:
            tuple[bool, str]: A tuple containing (is_valid, error_message).
        """
        # 1. Handle empty input (User reset the search -> "All areas")
        if not plz_input:
            return True, ""

        # 2. Check format: Digits only
        if not plz_input.isdigit():
            return False, "⚠️ Invalid Format: Input must contain only digits."

        # 3. Check format: Length (German PLZ are 5 digits)
        if len(plz_input) != 5:
            return False, "⚠️ Invalid Format: Postal code must be exactly 5 digits."

        # 4. Check domain validity: Is it in Berlin?
        plz_int = int(plz_input)
        if plz_int not in self.valid_plzs:
            return False, f"⚠️ Out of Scope: PLZ {plz_input} is not within the Berlin area."

        return True, ""

    def _handle_search(self, selected_plz: str):
        """
        Get options for sidebar filters and selections.

        Args:
            selected_plz (str): Selected postal code from sidebar.

        Returns:
            Dict of options for sidebar.
        """
        postal_code_area = None
        resident_data = None

        if selected_plz and selected_plz != "All areas":
            postal_code_object = PostalCode(selected_plz)

            # Use Case: Search stations by postal code (returns aggregate).
            postal_code_area = self.charging_station_service.search_by_postal_code(postal_code_object)

            # Use Case: Get residents count for postal code.
            resident_data = self.postal_code_residents_service.get_resident_data(postal_code_object)

        return (postal_code_area, resident_data)

    def _render_sidebar(self):
        """
        Render sidebar with search and filter options.
        """

        streamlit.sidebar.header("🔍 View Options")

        # Postal code search.
        streamlit.sidebar.markdown("---")
        streamlit.sidebar.subheader("📍 Search by Postal Code")

        # Replace selectbox with text_input for flexible entry and validation
        plz_input = streamlit.sidebar.text_input(
            "Enter Postal Code:",
            key="postal_code_input",
            help="Enter a 5-digit Berlin Postal Code (e.g., 10117) or leave empty for all areas.",
        )

        # Perform Validation
        is_valid, error_msg = self._validate_plz_input(plz_input)

        selected_plz = "All areas"  # Default

        if not is_valid:
            streamlit.sidebar.error(error_msg)
            # Stop processing search if invalid
            postal_code_area = None
            resident_data = None
        else:
            if plz_input:
                selected_plz = plz_input

            # Store in session state.
            streamlit.session_state["selected_plz"] = selected_plz

            postal_code_area, resident_data = self._handle_search(selected_plz)

            if postal_code_area and resident_data:
                info_parts = []
                info_parts.append(f"👥 Pop: {resident_data.get_population():,}")
                info_parts.append(f"⚡ Stations: {postal_code_area.station_count}")
                streamlit.sidebar.info("\n\n".join(info_parts))
            elif selected_plz != "All areas":
                # Handle edge case where PLZ is valid geodata but has no resident/station data
                streamlit.sidebar.warning(f"PLZ {selected_plz} is valid, but no data available.")

        # Visualization mode view options.
        streamlit.sidebar.markdown("---")
        view_mode = streamlit.sidebar.radio("Visualization Mode", ["Basic View", "Power Capacity (KW) View"])

        # Check if view mode changed
        previous_view_mode = streamlit.session_state.get("view_mode", "Basic View")
        view_mode_changed = previous_view_mode != view_mode

        # Store view mode in session state
        streamlit.session_state["view_mode"] = view_mode

        if view_mode == "Basic View":
            layer_options = ["Residents", "All Charging Stations"]
            # Reset layer selection if switching from Power Capacity view
            if view_mode_changed:
                streamlit.session_state["layer_selection"] = "All Charging Stations"
        else:
            layer_options = ["Power Capacity"]
            # Reset layer selection if switching to Power Capacity view
            if view_mode_changed:
                streamlit.session_state["layer_selection"] = "Power Capacity"

            # Add capacity range filter for Power Capacity view
            streamlit.sidebar.markdown("---")
            streamlit.sidebar.subheader("⚡ Capacity Range Filter")

            # Get current capacity filter or default to "All"
            current_capacity_filter = streamlit.session_state.get("capacity_filter", "All")

            capacity_filter = streamlit.sidebar.radio(
                "Filter by Capacity:",
                ["All", "Low", "Medium", "High"],
                index=["All", "Low", "Medium", "High"].index(current_capacity_filter),
                help="Filter postal codes by their total charging power capacity",
            )
            streamlit.session_state["capacity_filter"] = capacity_filter

        streamlit.sidebar.header("📊 Layer Selection")

        # Get current layer selection or use the first option as default
        current_layer = streamlit.session_state.get("layer_selection", layer_options[0])

        # Ensure current_layer is in layer_options, otherwise use first option
        if current_layer not in layer_options:
            current_layer = layer_options[0]

        layer_selection = streamlit.sidebar.radio(
            "Select Layer", layer_options, index=layer_options.index(current_layer)
        )
        streamlit.session_state["layer_selection"] = layer_selection

    def _render_about(self) -> None:
        """Render about/information view."""
        streamlit.header("ℹ️ About EVision Berlin")

        streamlit.markdown(ABOUT_SECTION)

    def _get_map_center_and_zoom(self, selected_postal_code: str):
        """
        Calculate map center and zoom level based on selected postal code.
        """

        if selected_postal_code in ("", "All areas"):
            return [52.52, 13.40], 10

        plz_geometry: GeoLocation = self.geolocation_service.get_geolocation_data_for_postal_code(
            PostalCode(selected_postal_code)
        )
        if plz_geometry is not None and not plz_geometry.empty:
            # Get the centroid of the boundary geometry
            centroid = plz_geometry.boundary.geometry.iloc[0].centroid
            return [centroid.y, centroid.x], 13

        return [52.52, 13.40], 10

    def _render_residents_layer(self, folium_map: folium.Map, selected_postal_code: str):
        """
        Render population density visualization on the map.

        For "All areas": Shows all postal codes colored by population density.
        For specific postal code: Highlights that area with population data.

        Args:
            folium_map (folium.Map): The Folium map object to add layer to.
            selected_postal_code (str): The selected postal code to display.
        """
        try:
            if selected_postal_code and selected_postal_code not in ("", "All areas"):
                # Render specific postal code
                logger.info("=== Rendering residents layer for PLZ: %s ===", selected_postal_code)
                postal_code_obj = PostalCode(selected_postal_code)

                # Get the postal code boundary area
                logger.info("Fetching geolocation data for %s...", selected_postal_code)
                plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                # Get resident data for the postal code
                resident_data = self.postal_code_residents_service.get_resident_data(postal_code_obj)

                if plz_geometry is not None and plz_geometry.boundary is not None and resident_data:
                    try:
                        population = resident_data.get_population()

                        # Convert the boundary GeoDataFrame to GeoJSON format
                        logger.info("Converting boundary to GeoJSON...")
                        boundary_geojson = json.loads(plz_geometry.boundary.to_json())
                        logger.info("GeoJSON conversion successful for residents layer")

                        # Add the postal code boundary with population styling
                        logger.info("Adding GeoJSON to folium map with population data...")
                        folium.GeoJson(
                            boundary_geojson,
                            name=f"Postal Code {selected_postal_code}",
                            style_function=lambda x: {
                                "fillColor": "#ff9800",  # Orange color for residents
                                "color": "#f57c00",  # Darker orange border
                                "weight": 2,
                                "fillOpacity": 0.5,
                            },
                            tooltip=f"Postal Code: {selected_postal_code}<br>👥 Population: {population:,}",
                        ).add_to(folium_map)

                        logger.info("✓ Postal code boundary with population data added to map successfully!")
                    except Exception as boundary_error:
                        logger.error("Error rendering residents boundary: %s", boundary_error, exc_info=True)
                        streamlit.error(f"Error rendering postal code boundary: {boundary_error}")
                else:
                    logger.warning(
                        "Cannot render residents layer - plz_geometry: %s, resident_data: %s",
                        plz_geometry,
                        resident_data,
                    )
                    streamlit.warning(f"No resident data available for postal code {selected_postal_code}")
            else:
                # Render all postal codes colored by population
                logger.info("=== Rendering all postal codes by population ===")

                # Get all postal codes
                postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

                # Collect population data for all postal codes
                population_data = []
                for postal_code in postal_codes:
                    resident_data = self.postal_code_residents_service.get_resident_data(postal_code)
                    if resident_data:
                        population_data.append(
                            {"postal_code": postal_code.value, "population": resident_data.get_population()}
                        )

                if not population_data:
                    streamlit.warning("No population data available for visualization.")
                    return

                # Create DataFrame and calculate color scale based on population
                pop_df = pd.DataFrame(population_data)
                max_population = pop_df["population"].max()
                min_population = pop_df["population"].min()

                areas_rendered = 0

                # Render each postal code area colored by population
                for _, row in pop_df.iterrows():
                    try:
                        plz = row["postal_code"]
                        population = row["population"]

                        postal_code_obj = PostalCode(plz)
                        plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                        if plz_geometry is not None and plz_geometry.boundary is not None:
                            # Get station count for this postal code
                            postal_code_area = self.charging_station_service.search_by_postal_code(postal_code_obj)
                            station_count = postal_code_area.station_count if postal_code_area else 0

                            # Calculate color based on population (orange gradient)
                            # Higher population = darker orange
                            normalized = (
                                (population - min_population) / (max_population - min_population)
                                if max_population > min_population
                                else 0.5
                            )

                            # Color gradient from light orange to dark orange
                            # Light: #ffe0b2 (RGB: 255, 224, 178)
                            # Dark: #e65100 (RGB: 230, 81, 0)
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
                                    f"Postal Code: {plz}<br>"
                                    f"👥 Population: {population:,}<br>"
                                    f"⚡ Stations: {station_count}"
                                ),
                            ).add_to(folium_map)
                            areas_rendered += 1
                    except Exception as e:
                        logger.warning("Could not render postal code %s: %s", plz, e)

                logger.info("✓ Rendered %d postal code areas by population", areas_rendered)

        except Exception as e:
            # Handle and display any errors gracefully in the UI
            logger.error("Error loading residents layer: %s", e, exc_info=True)
            streamlit.error(f"Error loading residents layer: {e}")

    def _render_power_capacity_layer(
        self, folium_map: folium.Map, selected_postal_code: str, capacity_filter: str = "All"
    ):
        """
        Render power capacity visualization on the map.

        For "All areas": Shows all postal code areas colored by total power capacity.
        For specific postal code: Highlights that area with capacity information.

        Args:
            folium_map (folium.Map): The Folium map object to add layers to.
            selected_postal_code (str): The selected postal code or "All areas".
            capacity_filter (str): Filter by capacity category ('All', 'Low', 'Medium', 'High').
        """
        try:
            # Get all postal codes
            postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

            # Calculate power capacity for all postal codes
            capacity_df = self.power_capacity_service.get_power_capacity_by_postal_code(postal_codes)

            # Classify capacity ranges
            range_definitions, capacity_df = self.power_capacity_service.classify_capacity_ranges(capacity_df)

            # Apply capacity filter
            if capacity_filter != "All":
                capacity_df = self.power_capacity_service.filter_by_capacity_category(capacity_df, capacity_filter)

            if capacity_df.empty:
                streamlit.warning(f"No postal codes found in the '{capacity_filter}' capacity range.")
                return

            max_capacity = capacity_df["total_capacity_kw"].max()

            # Display capacity range information
            if selected_postal_code in ("All areas", ""):
                streamlit.info(
                    f"**Power Capacity Ranges:**\n\n"
                    f"🟦 Low: {range_definitions['Low'][0]:.0f} - {range_definitions['Low'][1]:.0f} kW\n\n"
                    f"🔵 Medium: {range_definitions['Medium'][0]:.0f} - {range_definitions['Medium'][1]:.0f} kW\n\n"
                    f"🔷 High: {range_definitions['High'][0]:.0f} - {range_definitions['High'][1]:.0f} kW"
                )

            # Render postal code areas with capacity coloring
            if selected_postal_code and selected_postal_code not in ("", "All areas"):
                # Render specific postal code area
                postal_code_obj = PostalCode(selected_postal_code)
                plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                # Get capacity data for this postal code
                plz_capacity = capacity_df[capacity_df["postal_code"] == selected_postal_code]

                if plz_geometry is not None and plz_geometry.boundary is not None and not plz_capacity.empty:
                    capacity_value = plz_capacity.iloc[0]["total_capacity_kw"]
                    station_count = plz_capacity.iloc[0]["station_count"]
                    capacity_category = plz_capacity.iloc[0]["capacity_category"]

                    color = self.power_capacity_service.get_color_for_capacity(capacity_value, max_capacity)

                    boundary_geojson = json.loads(plz_geometry.boundary.to_json())
                    folium.GeoJson(
                        boundary_geojson,
                        name=f"Postal Code {selected_postal_code}",
                        style_function=lambda x, color=color: {
                            "fillColor": color,
                            "color": "#000000",
                            "weight": 2,
                            "fillOpacity": 0.7,
                        },
                        tooltip=(
                            f"Postal Code: {selected_postal_code}<br>"
                            f"Total Capacity: {capacity_value:.0f} kW<br>"
                            f"Stations: {station_count}<br>"
                            f"Category: {capacity_category}"
                        ),
                    ).add_to(folium_map)
                else:
                    streamlit.warning(f"No capacity data available for postal code {selected_postal_code}")
            else:
                # Render all postal code areas
                areas_rendered = 0
                for _, row in capacity_df.iterrows():
                    plz = row["postal_code"]
                    capacity = row["total_capacity_kw"]
                    station_count = row["station_count"]
                    category = row["capacity_category"]

                    postal_code_obj = PostalCode(plz)
                    plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                    if plz_geometry is not None and plz_geometry.boundary is not None:
                        try:
                            color = self.power_capacity_service.get_color_for_capacity(capacity, max_capacity)
                            boundary_geojson = json.loads(plz_geometry.boundary.to_json())

                            folium.GeoJson(
                                boundary_geojson,
                                name=f"PLZ {plz}",
                                style_function=lambda x, color=color: {
                                    "fillColor": color,
                                    "color": "#666666",
                                    "weight": 1,
                                    "fillOpacity": 0.7,
                                },
                                tooltip=(
                                    f"Postal Code: {plz}<br>"
                                    f"Total Capacity: {capacity:.0f} kW<br>"
                                    f"Stations: {station_count}<br>"
                                    f"Category: {category}"
                                ),
                            ).add_to(folium_map)
                            areas_rendered += 1
                        except Exception as e:
                            logger.warning("Could not render postal code %s: %s", plz, e)
        except Exception as e:
            logger.error("Error rendering power capacity layer: %s", e, exc_info=True)
            streamlit.error(f"Error rendering power capacity layer: {e}")

    def _render_charging_stations_layer(self, folium_map: folium.Map, selected_postal_code: str):
        """
        Render charging station markers and postal code boundary on the map for the selected area.

        This method visualizes:
        - For specific postal code: Postal code area boundary (blue shaded polygon) + Individual charging stations
        - For "All areas": All postal codes colored by number of charging stations

        Args:
            folium_map (folium.Map): The Folium map object to add markers to.
            selected_postal_code (str): The postal code to display stations for.

        Raises:
            Displays error message in UI if station data cannot be loaded.
        """
        try:
            if selected_postal_code and selected_postal_code not in ("", "All areas"):
                # Render specific postal code with stations
                logger.info("=== Starting to render charging stations layer for PLZ: %s ===", selected_postal_code)
                postal_code_obj = PostalCode(selected_postal_code)

                # Get and render the postal code boundary area
                logger.info("Fetching geolocation data for %s...", selected_postal_code)
                plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                logger.info("plz_geometry is None: %s", plz_geometry is None)
                if plz_geometry is not None:
                    logger.info("plz_geometry type: %s", type(plz_geometry))
                    logger.info("plz_geometry.boundary is None: %s", plz_geometry.boundary is None)
                    if plz_geometry.boundary is not None:
                        logger.info("plz_geometry.boundary type: %s", type(plz_geometry.boundary))
                        logger.info("plz_geometry.boundary shape: %s", plz_geometry.boundary.shape)
                        logger.info("plz_geometry.boundary columns: %s", plz_geometry.boundary.columns.tolist())
                        logger.info("First few rows:\n%s", plz_geometry.boundary.head())
                if plz_geometry is not None and plz_geometry.boundary is not None:
                    try:
                        # Convert the boundary GeoDataFrame to GeoJSON format
                        # The boundary is stored as a GeoDataFrame, access its geometry
                        logger.info("Converting boundary to GeoJSON...")
                        boundary_geojson = json.loads(plz_geometry.boundary.to_json())
                        logger.info("GeoJSON conversion successful. Type: %s", type(boundary_geojson))
                        geojson_keys = boundary_geojson.keys() if isinstance(boundary_geojson, dict) else "Not a dict"
                        logger.info("GeoJSON keys: %s", geojson_keys)
                        logger.info("GeoJSON content (first 500 chars): %s", str(boundary_geojson)[:500])
                        # Add the postal code boundary as a shaded area
                        logger.info("Adding GeoJSON to folium map...")
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
                    boundary_info = plz_geometry.boundary if plz_geometry else "N/A"
                    logger.warning(
                        "Cannot render boundary - plz_geometry: %s, boundary: %s", plz_geometry, boundary_info
                    )
                    streamlit.warning(f"No boundary data available for postal code {selected_postal_code}")

                # Retrieve stations for the selected postal code area
                logger.info("Fetching charging stations for %s...", selected_postal_code)
                stations = self.charging_station_service.find_stations_by_postal_code(postal_code_obj)
                logger.info("Found %d charging stations", len(stations))

                # Create interactive map marker for each charging station
                for station in stations:
                    folium.CircleMarker(
                        location=[station.latitude, station.longitude],
                        radius=6,
                        popup=f"PLZ: {station.postal_code.value}<br>Power: {station.power_capacity.kilowatts} kW",
                        color="darkgreen",
                        fill=True,
                        fillColor="green",
                        fillOpacity=0.8,
                    ).add_to(folium_map)
            else:
                # Render all postal codes colored by station count
                logger.info("=== Rendering all postal codes by charging station count ===")

                # Get all postal codes
                postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

                # Collect station count data for all postal codes
                station_data = []
                for postal_code in postal_codes:
                    postal_code_area = self.charging_station_service.search_by_postal_code(postal_code)
                    station_count = postal_code_area.station_count if postal_code_area else 0

                    # Get population data as well
                    resident_data = self.postal_code_residents_service.get_resident_data(postal_code)
                    population = resident_data.get_population() if resident_data else 0

                    station_data.append(
                        {"postal_code": postal_code.value, "station_count": station_count, "population": population}
                    )

                if not station_data:
                    streamlit.warning("No charging station data available for visualization.")
                    return

                # Create DataFrame and calculate color scale based on station count
                stations_df = pd.DataFrame(station_data)
                max_stations = stations_df["station_count"].max()
                min_stations = stations_df["station_count"].min()

                areas_rendered = 0

                # Render each postal code area colored by station count
                for _, row in stations_df.iterrows():
                    try:
                        plz = row["postal_code"]
                        station_count = row["station_count"]
                        population = row["population"]

                        postal_code_obj = PostalCode(plz)
                        plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                        if plz_geometry is not None and plz_geometry.boundary is not None:
                            # Calculate color based on station count (green gradient)
                            # More stations = darker green
                            if max_stations > min_stations:
                                normalized = (station_count - min_stations) / (max_stations - min_stations)
                            else:
                                normalized = 0.5

                            # Color gradient from light green to dark green
                            # Light: #c8e6c9 (RGB: 200, 230, 201)
                            # Dark: #1b5e20 (RGB: 27, 94, 32)
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
                                    f"Postal Code: {plz}<br>"
                                    f"👥 Population: {population:,}<br>"
                                    f"⚡ Stations: {station_count}"
                                ),
                            ).add_to(folium_map)
                            areas_rendered += 1
                    except Exception as e:
                        logger.warning("Could not render postal code %s: %s", plz, e)

                logger.info("✓ Rendered %d postal code areas by station count", areas_rendered)

        except Exception as e:
            # Handle and display any errors gracefully in the UI
            logger.error("Error loading charging stations: %s", e, exc_info=True)
            streamlit.error(f"Error loading charging stations: {e}")

    def _render_map_view(self, selected_postal_code: str, layer_selection: str):
        """
        Render interactive map view with user-selected data layers.

        Creates a Folium map centered on the selected area and overlays
        the chosen visualization layer (residents, charging stations, or power capacity).

        Args:
            selected_postal_code (str): Postal code to center map on.
            layer_selection (str): Layer type to display ("Residents", "All Charging Stations", or "Power Capacity").
        """
        # Calculate optimal map center and zoom level for selected area
        map_center, map_zoom = self._get_map_center_and_zoom(selected_postal_code)
        folium_map = folium.Map(location=map_center, zoom_start=map_zoom)

        # Render the appropriate data layer based on user selection
        if layer_selection == "Residents":
            self._render_residents_layer(folium_map, selected_postal_code)
        elif layer_selection == "All Charging Stations":
            self._render_charging_stations_layer(folium_map, selected_postal_code)
        elif layer_selection == "Power Capacity":
            capacity_filter = streamlit.session_state.get("capacity_filter", "All")
            self._render_power_capacity_layer(folium_map, selected_postal_code, capacity_filter)

        # Display the map in Streamlit with responsive dimensions
        folium_static(folium_map, width=1400, height=800)

    def _render_demand_map(self, folium_map: folium.Map, selected_postal_code: str):
        """
        Render demand analysis map with color-coded priority levels for all postal codes.

        This method visualizes demand priority across Berlin by coloring postal code areas:
        - High Priority (Red): > 5000 residents per station
        - Medium Priority (Yellow/Gold): 2000-5000 residents per station
        - Low Priority (Green): < 2000 residents per station

        Args:
            folium_map (folium.Map): The Folium map object to add the visualization to.
            selected_postal_code (str): Currently selected postal code (used for highlighting).
        """
        try:
            # Get all postal codes for analysis
            postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

            # Collect data and perform demand analysis
            areas_data = []
            for postal_code in postal_codes:
                resident_data = self.postal_code_residents_service.get_resident_data(postal_code)
                postal_code_area = self.charging_station_service.search_by_postal_code(postal_code)

                if resident_data and postal_code_area:
                    areas_data.append(
                        {
                            "postal_code": postal_code.value,
                            "population": resident_data.get_population(),
                            "station_count": postal_code_area.station_count,
                        }
                    )

            if not areas_data:
                streamlit.warning("No data available for demand map visualization.")
                return

            # Perform batch analysis
            results = self.demand_analysis_service.analyze_multiple_areas(areas_data)

            # Define color mapping for priorities
            priority_colors = {
                "High": "#ff6b6b",  # Red for high priority
                "Medium": "#ffd93d",  # Gold/Yellow for medium priority
                "Low": "#6bcf7f",  # Green for low priority
            }

            areas_rendered = 0

            # Render each postal code area with color-coded priority
            for analysis in results:
                try:
                    plz = analysis.postal_code
                    priority = analysis.demand_priority
                    postal_code_obj = PostalCode(plz)

                    # Get geometry for the postal code
                    plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                    if plz_geometry is not None and plz_geometry.boundary is not None:
                        # Get color based on priority level
                        fill_color = priority_colors.get(priority, "#cccccc")

                        # Add border emphasis if this is the selected postal code
                        border_color = "#000000" if plz == selected_postal_code else "#666666"
                        border_weight = 3 if plz == selected_postal_code else 1

                        # Convert boundary to GeoJSON
                        boundary_geojson = json.loads(plz_geometry.boundary.to_json())

                        # Get demand metrics from DTO
                        urgency_score = analysis.urgency_score
                        residents_per_station = analysis.residents_per_station

                        # Create tooltip with demand analysis info
                        tooltip_html = (
                            f"<b>Postal Code: {plz}</b><br>"
                            f"Priority: {priority}<br>"
                            f"Population: {analysis.population:,}<br>"
                            f"Stations: {analysis.station_count}<br>"
                            f"Residents/Station: {residents_per_station:.0f}<br>"
                            f"Urgency Score: {urgency_score:.0f}/100"
                        )

                        # Add GeoJSON layer to map
                        folium.GeoJson(
                            boundary_geojson,
                            name=f"PLZ {plz} - {priority}",
                            style_function=lambda x, color=fill_color, border=border_color, weight=border_weight: {
                                "fillColor": color,
                                "color": border,
                                "weight": weight,
                                "fillOpacity": 0.7,
                            },
                            tooltip=tooltip_html,
                        ).add_to(folium_map)
                        areas_rendered += 1
                except Exception as e:
                    logger.warning("Could not render demand map for postal code: %s", e)
                    logger.exception(e)

        except Exception as e:
            logger.error("Error rendering demand analysis map: %s", e, exc_info=True)
            streamlit.error(f"Error rendering demand analysis map: {e}")

    def _render_demand_analysis(self, selected_postal_code: str):
        """
        Render comprehensive demand analysis dashboard with priority assessment.

        This method implements the complete demand analysis view, providing:
        - Interactive map with color-coded priority levels
        - Detailed metrics for individual postal code areas
        - Infrastructure recommendations based on demand priority
        - Comprehensive overview table for all areas
        - Summary statistics with visual priority indicators

        The analysis uses the Demand bounded context to calculate priority levels
        based on population-to-station ratios, following industry best practices.

        Args:
            selected_postal_code (str): The postal code selected for detailed analysis.
                                       Use "All areas" for overview only.

        Analysis Workflow:
            1. Display interactive map with color-coded priorities
            2. Collect population and station data for all areas
            3. Perform batch demand analysis via DemandAnalysisService
            4. Display detailed metrics for selected area (if applicable)
            5. Show high-priority areas requiring immediate attention
            6. Present complete overview with color-coded priorities
            7. Provide summary statistics
        """
        streamlit.header("📊 EV Charging Infrastructure Demand Analysis")
        streamlit.markdown("*Analyzing population density and charging station coverage*")

        # Render demand priority map
        streamlit.subheader("🗺️ Demand Priority Map")

        # Create map centered on Berlin
        center, zoom = self._get_map_center_and_zoom(selected_postal_code)
        demand_map = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

        # Display legend below the map
        col1, col2, col3 = streamlit.columns([2, 2, 2])
        with col1:
            streamlit.markdown("🔴 **High Priority** - >5000 residents/station")
        with col2:
            streamlit.markdown("🟡 **Medium Priority** - 2000-5000 residents/station")
        with col3:
            streamlit.markdown("🟢 **Low Priority** - <2000 residents/station")

        # Render the demand analysis layer
        self._render_demand_map(demand_map, selected_postal_code)

        # Display the map
        folium_static(demand_map, width=1400, height=600)

        # Retrieve all postal codes for comprehensive analysis
        postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

        # Collect data for demand analysis from both resident and station services
        areas_data = []
        for postal_code in postal_codes:
            resident_data = self.postal_code_residents_service.get_resident_data(postal_code)
            postal_code_area = self.charging_station_service.search_by_postal_code(postal_code)

            if resident_data and postal_code_area:
                areas_data.append(
                    {
                        "postal_code": postal_code.value,
                        "population": resident_data.get_population(),
                        "station_count": postal_code_area.station_count,
                    }
                )

        # Perform batch analysis
        if areas_data:
            analyses = self.demand_analysis_service.analyze_multiple_areas(areas_data)
            # If specific postal code selected, show detailed analysis
            if selected_postal_code and selected_postal_code != "All areas":
                streamlit.subheader(f"🔍 Detailed Analysis: {selected_postal_code}")

                # Get specific analysis
                analysis = self.demand_analysis_service.get_demand_analysis(selected_postal_code)

                if analysis:

                    # Display metrics in columns
                    col1, col2, col3, col4 = streamlit.columns(4)

                    with col1:
                        streamlit.metric("Population", f"{analysis.population:,}")

                    with col2:
                        streamlit.metric("Charging Stations", analysis.station_count)

                    with col3:
                        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(
                            analysis.demand_priority, "⚪"
                        )
                        streamlit.metric("Priority", f"{priority_color} {analysis.demand_priority}")

                    with col4:
                        streamlit.metric("Residents/Station", f"{analysis.residents_per_station:.0f}")

                    # Coverage assessment
                    streamlit.markdown("---")
                    col_assess1, col_assess2, col_assess3 = streamlit.columns(3)

                    with col_assess1:
                        streamlit.info(f"**Coverage Assessment**\n\n{analysis.coverage_assessment}")

                    with col_assess2:
                        streamlit.info(f"**Urgency Score**\n\n{analysis.urgency_score:.0f}/100")

                    with col_assess3:
                        expansion_status = "✅ Yes" if analysis.needs_expansion else "❌ No"
                        streamlit.info(f"**Needs Expansion**\n\n{expansion_status}")

                    # Recommendations
                    streamlit.markdown("---")
                    streamlit.subheader("💡 Recommendations")

                    recommendations = self.demand_analysis_service.get_recommendations(
                        selected_postal_code, target_ratio=2000.0
                    )

                    if recommendations["recommended_additional_stations"] > 0:
                        streamlit.warning(
                            f"🚨 **Action Needed**: This area requires approximately "
                            f"**{recommendations['recommended_additional_stations']} additional charging stations** "
                            f"to meet the target ratio of 2,000 residents per station."
                        )
                    else:
                        streamlit.success("✅ This area has adequate charging infrastructure coverage.")

                    streamlit.markdown(
                        f"""
                    **Infrastructure Status:**
                    - Current stations: {recommendations['current_stations']}
                    - Recommended total: {recommendations['recommended_total_stations']}
                    - Current ratio: {recommendations['current_ratio']:.0f} residents/station
                    - Target ratio: {recommendations['target_ratio']:.0f} residents/station
                    """
                    )
                else:
                    streamlit.warning(f"No analysis data available for {selected_postal_code}")

            # Show overview table
            streamlit.markdown("---")
            streamlit.subheader("📋 Overview: All Postal Code Areas")

            # Get high priority areas
            high_priority_areas = self.demand_analysis_service.get_high_priority_areas()
            high_priority_dicts = [area.to_dict() for area in high_priority_areas]

            if high_priority_dicts:
                streamlit.markdown(f"**🔴 {len(high_priority_dicts)} High Priority Areas Identified**")

                # Display high priority areas
                high_priority_df = pd.DataFrame(high_priority_dicts)
                high_priority_df = high_priority_df[
                    [
                        "postal_code",
                        "population",
                        "station_count",
                        "residents_per_station",
                        "urgency_score",
                        "coverage_assessment",
                    ]
                ]
                high_priority_df.columns = [
                    "Postal Code",
                    "Population",
                    "Stations",
                    "Residents/Station",
                    "Urgency Score",
                    "Coverage",
                ]
                high_priority_df = high_priority_df.sort_values("Urgency Score", ascending=False)

                streamlit.dataframe(high_priority_df, width="stretch", hide_index=True)

            # Display overview table with color-coded priority visualization
            streamlit.markdown("---")
            streamlit.subheader("📊 All Areas Analysis")

            results_dicts = [analysis.to_dict() for analysis in analyses]
            results_df = pd.DataFrame(results_dicts)
            results_df = results_df[
                [
                    "postal_code",
                    "population",
                    "station_count",
                    "demand_priority",
                    "residents_per_station",
                    "coverage_assessment",
                ]
            ]
            results_df.columns = ["Postal Code", "Population", "Stations", "Priority", "Residents/Station", "Coverage"]

            # Sort by priority level and then by residents per station ratio
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            results_df["priority_rank"] = results_df["Priority"].map(priority_order)
            results_df = results_df.sort_values(["priority_rank", "Residents/Station"], ascending=[True, False])
            results_df = results_df.drop("priority_rank", axis=1)

            # Apply professional color scheme for enhanced readability
            def highlight_priority(row):
                """
                Apply color-coded styling to table rows based on demand priority.

                Color Scheme:
                    - High Priority: Dark red (#ff6b6b) with white bold text
                    - Medium Priority: Gold (#ffd93d) with black bold text
                    - Low Priority: Green (#6bcf7f) with white bold text

                Args:
                    row: DataFrame row to style.

                Returns:
                    List of CSS style strings for each cell in the row.
                """

                if row["Priority"] == "High":
                    return ["background-color: #ff6b6b; color: white; font-weight: bold"] * len(row)
                if row["Priority"] == "Medium":
                    return ["background-color: #ffd93d; color: black; font-weight: bold"] * len(row)
                return ["background-color: #6bcf7f; color: white; font-weight: bold"] * len(row)

            styled_df = results_df.style.apply(highlight_priority, axis=1)

            streamlit.dataframe(styled_df, width="stretch", hide_index=True)

            # Summary statistics
            streamlit.markdown("---")
            streamlit.subheader("📈 Summary Statistics")

            col_stat1, col_stat2, col_stat3 = streamlit.columns(3)

            high_count = len([r for r in analyses if r.demand_priority == "High"])
            medium_count = len([r for r in analyses if r.demand_priority == "Medium"])
            low_count = len([r for r in analyses if r.demand_priority == "Low"])

            with col_stat1:
                streamlit.metric("🔴 High Priority Areas", high_count)

            with col_stat2:
                streamlit.metric("🟡 Medium Priority Areas", medium_count)

            with col_stat3:
                streamlit.metric("🟢 Low Priority Areas", low_count)

        else:
            streamlit.warning("No data available for demand analysis.")

    def _render_main_content(self):
        """
        Render main content area.
        """

        # Get session state.
        selected_plz = streamlit.session_state.get("selected_plz", "All areas")
        view_mode = streamlit.session_state.get("view_mode", "Basic View")

        # Get layer selection with appropriate default based on view mode
        if view_mode == "Power Capacity (KW) View":
            layer_selection = streamlit.session_state.get("layer_selection", "Power Capacity")
        else:
            layer_selection = streamlit.session_state.get("layer_selection", "All Charging Stations")

        main_tab, demand_analysis_tab, about_tab = streamlit.tabs(["🗺️ Map View", "📊 Demand Analysis", "ℹ️ About"])
        with main_tab:
            self._render_map_view(selected_plz, layer_selection)

        with demand_analysis_tab:
            self._render_demand_analysis(selected_plz)

        with about_tab:
            self._render_about()

    def run(self):
        """
        Run the Streamlit application.
        """

        # Page configuration.
        streamlit.set_page_config(layout="wide", page_title="EVision Berlin Infrastructure")

        # Title.
        streamlit.title("Berlin Electric Vehicle Infrastructure Analysis")
        streamlit.markdown("*Powered by Domain-Driven Design & Test-Driven Development*")

        # Sidebar.
        self._render_sidebar()

        # Main content.
        self._render_main_content()
