"""
Streamlit Application for EVision Berlin.
"""

from typing import List

import folium
import streamlit

from streamlit_folium import folium_static

from src.shared.domain.events import DomainEventBus
from src.shared.domain.entities import ChargingStation
from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.application.services import ChargingStationService, GeoLocationService, PostalCodeResidentService
from src.demand.application.services import DemandAnalysisService
from src.discovery.domain.aggregates import PostalCodeAreaAggregate


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
        event_bus: DomainEventBus,
    ):
        """
        Initialize EVision Berlin Streamlit application.

        Args:
            postal_code_residents_service (PostalCodeResidentService): Service for postal code residents.
            charging_station_service (ChargingStationService): Service for charging stations.
            geolocation_service (GeoLocationService): Service for geolocation data.
            demand_analysis_service (DemandAnalysisService): Service for demand analysis.
            event_bus (DomainEventBus): Domain event bus.
        """

        self.postal_code_residents_service = postal_code_residents_service
        self.charging_station_service = charging_station_service
        self.geolocation_service = geolocation_service
        self.demand_analysis_service = demand_analysis_service
        self.event_bus = event_bus

    def _handle_search(self, selected_plz: str):
        """
        Get options for sidebar filters and selections.

        Args:
            selected_plz (str): Selected postal code from sidebar.

        Returns:
            Dict of options for sidebar.
        """

        # TODO: Add validation failure case.
        postal_code_area = None
        resident_data = None
        if selected_plz != "All areas":
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

        # Query: Get all available postal codes
        postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)
        postal_code_options = ["All areas"] + PostalCode.get_values(postal_codes)
        selected_plz = streamlit.sidebar.selectbox(
            "Select Postal Code:", options=postal_code_options, key="postal_code_search"
        )

        # Store in session state.
        streamlit.session_state["selected_plz"] = selected_plz

        postal_code_area, resident_data = self._handle_search(selected_plz)
        if postal_code_area and resident_data:
            info_parts = []
            info_parts.append(f"👥 Pop: {resident_data.get_population():,}")
            info_parts.append(f"⚡ Stations: {postal_code_area.get_station_count()}")
            streamlit.sidebar.info("\n\n".join(info_parts))

        # Visualization mode view options.
        streamlit.sidebar.markdown("---")
        view_mode = streamlit.sidebar.radio("Visualization Mode", ["Basic View", "Power Capacity (KW) View"])
        if view_mode == "Basic View":
            layer_options = ["Residents", "All Charging Stations"]
        else:
            layer_options = ["Residents"]
            # if dfr_by_kw:
            #     layer_options.extend(list(dfr_by_kw.keys()))

        streamlit.sidebar.header("📊 Layer Selection")
        streamlit.sidebar.radio("Select Layer", layer_options)

        streamlit.sidebar.markdown("---")
        streamlit.sidebar.checkbox("📈 Show Demand Analysis", value=False)

    # TODO: Needs rework. This is AI generated :)
    def _render_about(self) -> None:
        """Render about/information view."""
        streamlit.header("ℹ️ About EVision Berlin")

        streamlit.markdown(
            """
        ### Domain-Driven Design Architecture

        This application is built using **Domain-Driven Design (DDD)** principles with **Test-Driven Development (TDD)**:

        #### 🎯 Bounded Contexts

        1. **Station Discovery Context**
           - Manages charging station data and search operations
           - Uses value objects: PostalCode, GeoLocation, PowerCapacity
           - Provides station search by postal code

        2. **Demand Analysis Context**
           - Analyzes EV charging infrastructure demand
           - Calculates priority levels based on population and station density
           - Identifies high-priority areas for infrastructure expansion

        3. **Shared Kernel**
           - Common value objects used across contexts
           - Domain event system for loose coupling

        #### 🏗️ Architecture Layers

        - **Domain Layer**: Business logic and entities
        - **Application Layer**: Use case orchestration
        - **Infrastructure Layer**: Data access (CSV repositories)
        - **UI Layer**: Streamlit presentation (this app)

        #### ✅ Test Coverage

        - 100+ unit tests covering all domain logic
        - TDD approach: tests written before implementation
        - Continuous validation of business rules

        #### 📊 Data Sources

        - **Ladesäulenregister**: Charging station data from BNetzA
        - **PLZ Einwohner**: Population data by postal code
        - **Geodata Berlin**: Geographic boundary data

        ---

        **Version**: 2.0 (DDD Architecture)  
        **Framework**: Streamlit + DDD + TDD  
        **Course**: Advanced Software Engineering
        """
        )

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
            centroid = plz_geometry.boundary.centroid
            return [centroid.y, centroid.x], 13

        return [52.52, 13.40], 10

    def _render_residents_layer(self):
        """
        Add residents heatmap layer to the map.
        """

    def _render_charging_stations_layer(self, selected_postal_code: str):
        """
        Add charging stations heatmap layer to the map.
        """

        areas = None
        if selected_postal_code not in ("", "All areas"):
            areas = PostalCodeAreaAggregate(postal_code=PostalCode(selected_postal_code))
        else:
            areas = self.charging_station_service.get_stations_for_all_postal_codes()

        stations: List[ChargingStation] = self.charging_station_service.find_stations_by_postal_code(
            PostalCode(selected_postal_code)
        )
        for station in stations:
            areas.add_station(station)

        # TODO: Adjust using actual aggregate or data.
        min_station_count = 0
        max_station_count = 0
        color_map = folium.LinearColormap(
            colors=["yellow", "red"],
            vmin=min_station_count,
            vmax=max_station_count,
        )

        for _, row in areas.iterrows():
            is_selected = selected_postal_code not in ("", "All areas") and row["PLZ"] == selected_postal_code
            folium.GeoJson(
                row["geometry"],
                style_function=lambda _, color=color_map(row["Number"]), is_sel=is_selected: {
                    "fillColor": color,
                    "color": "blue" if is_sel else "black",
                    "weight": 4 if is_sel else 1,
                    "fillOpacity": 0.9 if is_sel else 0.7,
                },
                tooltip=f"PLZ: {row['PLZ']}, Number: {row['Number']}" + (" ⭐ SELECTED" if is_selected else ""),
            ).add_to(map)

            color_map.add_to(map)

    def _render_map_view(self, selected_postal_code: str, layer_selection: str):
        """
        Render map view with charging stations and residents.

        """

        map_center, map_zoom = self._get_map_center_and_zoom(selected_postal_code)
        folium_map = folium.Map(location=map_center, zoom_start=map_zoom)

        # Render selected layer.
        if layer_selection == "Residents":
            self._render_residents_layer()
        elif layer_selection == "All Charging Stations":
            self._render_charging_stations_layer(selected_postal_code)
        # else:
        #     if self.dfr_by_kw and layer_selection in self.dfr_by_kw:
        #         self._render_kw_layer(map, self.dfr_by_kw[layer_selection], layer_selection, selected_postal_code)

        folium_static(folium_map, width=1400, height=800)

    def _render_demand_analysis(self, a):
        pass

    def _render_main_content(self):
        """
        Render main content area.
        """

        # Get session state.
        selected_plz = streamlit.session_state.get("selected_plz", "All areas")
        show_demand = streamlit.session_state.get("show_demand", True)

        main_tab, demand_analysis_tab, about_tab = streamlit.tabs(["🗺️ Map View", "📊 Demand Analysis", "ℹ️ About"])
        with main_tab:
            self._render_map_view(selected_plz, show_demand)

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
