"""
Streamlit Application for EVision Berlin.

This is a thin orchestrator that delegates to bounded context views,
following proper Domain-Driven Design (DDD) principles.
"""

import folium
import streamlit

from streamlit_folium import folium_static

from src.shared.infrastructure import get_logger
from src.shared.domain.events import IDomainEventPublisher
from src.shared.application.services import (
    ChargingStationService,
    GeoLocationService,
    PostalCodeResidentService,
    PowerCapacityService,
)
from src.demand.application.services import DemandAnalysisService

# Import bounded context views
from src.discovery.views import StationDiscoveryView, PowerCapacityView
from src.demand.views import DemandAnalysisView
from src.shared.views import AboutView, get_map_center_and_zoom, render_sidebar

logger = get_logger(__name__)


class StreamlitApp:  # pylint: disable=too-many-instance-attributes
    """
    Streamlit application orchestrator for EVision Berlin infrastructure analysis.

    This class provides a thin UI orchestration layer following DDD principles,
    delegating to bounded context views for actual rendering.

    Responsibilities:
    - Initialize and coordinate view components
    - Manage application lifecycle (setup, run)
    - Delegate rendering to appropriate bounded context views
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
            postal_code_residents_service: Service for postal code residents.
            charging_station_service: Service for charging stations.
            geolocation_service: Service for geolocation data.
            demand_analysis_service: Service for demand analysis.
            power_capacity_service: Service for power capacity analysis.
            event_bus: Domain event bus interface.
            valid_plzs: List of valid Berlin postal codes for validation.
        """
        # Store services and configuration
        self.postal_code_residents_service = postal_code_residents_service
        self.charging_station_service = charging_station_service
        self.geolocation_service = geolocation_service
        self.demand_analysis_service = demand_analysis_service
        self.power_capacity_service = power_capacity_service
        self.event_bus = event_bus
        self.valid_plzs = valid_plzs

        # Initialize bounded context views
        self.station_discovery_view = StationDiscoveryView(
            charging_station_service=charging_station_service,
            geolocation_service=geolocation_service,
            postal_code_residents_service=postal_code_residents_service,
        )

        self.power_capacity_view = PowerCapacityView(
            power_capacity_service=power_capacity_service,
            geolocation_service=geolocation_service,
            postal_code_residents_service=postal_code_residents_service,
        )

        self.demand_analysis_view = DemandAnalysisView(
            demand_analysis_service=demand_analysis_service,
            charging_station_service=charging_station_service,
            geolocation_service=geolocation_service,
            postal_code_residents_service=postal_code_residents_service,
        )

        self.about_view = AboutView()

    def _render_sidebar(self):
        """
        Render sidebar with search and filter options.

        Delegates to shared components for sidebar rendering.
        """
        return render_sidebar(
            postal_code_residents_service=self.postal_code_residents_service,
            charging_station_service=self.charging_station_service,
            valid_plzs=self.valid_plzs,
        )

    def _render_map_view(self, selected_postal_code: str, layer_selection: str):
        """
        Render interactive map view with user-selected data layers.

        Delegates to appropriate bounded context views based on layer selection.

        Args:
            selected_postal_code: Postal code to center map on.
            layer_selection: Layer type to display.
        """
        # Calculate optimal map center and zoom
        map_center, map_zoom = get_map_center_and_zoom(
            selected_postal_code, self.geolocation_service, default_center=[52.52, 13.40], default_zoom=10
        )
        folium_map = folium.Map(location=map_center, zoom_start=map_zoom)

        # Delegate to appropriate bounded context view
        if layer_selection == "Residents":
            self.station_discovery_view.render_residents_layer(folium_map, selected_postal_code)
        elif layer_selection == "All Charging Stations":
            self.station_discovery_view.render_charging_stations_layer(folium_map, selected_postal_code)
        elif layer_selection == "Power Capacity":
            capacity_filter = streamlit.session_state.get("capacity_filter", "All")
            self.power_capacity_view.render_power_capacity_layer(folium_map, selected_postal_code, capacity_filter)

        # Display the map
        folium_static(folium_map, width=1400, height=800)

    def _render_main_content(self):
        """
        Render main content area with tabs for different views.

        Orchestrates the display of map view, demand analysis, and about sections.
        """
        # Get session state
        selected_plz = streamlit.session_state.get("selected_plz", "All areas")
        view_mode = streamlit.session_state.get("view_mode", "Basic View")

        # Get layer selection with appropriate default
        if view_mode == "Power Capacity (KW) View":
            layer_selection = streamlit.session_state.get("layer_selection", "Power Capacity")
        else:
            layer_selection = streamlit.session_state.get("layer_selection", "All Charging Stations")

        # Create tabs and delegate to views
        main_tab, demand_analysis_tab, about_tab = streamlit.tabs(["🗺️ Map View", "📊 Demand Analysis", "ℹ️ About"])

        with main_tab:
            self._render_map_view(selected_plz, layer_selection)

        with demand_analysis_tab:
            self.demand_analysis_view.render_demand_analysis(selected_plz)

        with about_tab:
            self.about_view.render_about()

    def run(self):
        """
        Run the Streamlit application.

        Entry point for the application. Sets up page configuration and
        orchestrates the rendering of sidebar and main content.
        """
        # Page configuration
        streamlit.set_page_config(layout="wide", page_title="EVision Berlin Infrastructure")

        # Title
        streamlit.title("Berlin Electric Vehicle Infrastructure Analysis")
        streamlit.markdown("*Powered by Domain-Driven Design & Test-Driven Development*")

        # Render sidebar and main content
        self._render_sidebar()
        self._render_main_content()
