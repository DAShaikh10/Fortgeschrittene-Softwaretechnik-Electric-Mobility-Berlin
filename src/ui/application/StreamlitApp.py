"""
Streamlit Application for EVision Berlin.
"""

from typing import List
import json
import logging

import folium
import streamlit

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import pandas as pd


from streamlit_folium import folium_static

from src.shared.domain.events import DomainEventBus
from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.application.services import ChargingStationService, GeoLocationService, PostalCodeResidentService
from src.demand.application.services import DemandAnalysisService


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
            # Get the centroid of the boundary geometry
            centroid = plz_geometry.boundary.geometry.iloc[0].centroid
            return [centroid.y, centroid.x], 13

        return [52.52, 13.40], 10

    def _render_residents_layer(self, folium_map: folium.Map):
        """
        Render population density heatmap layer on the map.

        Args:
            folium_map (folium.Map): The Folium map object to add layer to.

        Note:
            This feature is planned for future implementation.
        """
        # TODO: Implement residents visualization using population data

    def _render_charging_stations_layer(self, folium_map: folium.Map, selected_postal_code: str):
        """
        Render charging station markers and postal code boundary on the map for the selected area.

        This method visualizes:
        - Postal code area boundary (blue shaded polygon)
        - Individual charging stations as interactive markers (green circles)

        Args:
            folium_map (folium.Map): The Folium map object to add markers to.
            selected_postal_code (str): The postal code to display stations for.

        Behavior:
            - For specific postal code: Displays postal code boundary and all stations in that area
            - For "All areas": Shows informational message (avoid map clutter)

        Raises:
            Displays error message in UI if station data cannot be loaded.
        """
        try:
            if selected_postal_code and selected_postal_code not in ("", "All areas"):
                logger.info(f"=== Starting to render charging stations layer for PLZ: {selected_postal_code} ===")
                postal_code_obj = PostalCode(selected_postal_code)
                
                # Get and render the postal code boundary area
                logger.info(f"Fetching geolocation data for {selected_postal_code}...")
                plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)
                
                logger.info(f"plz_geometry is None: {plz_geometry is None}")
                if plz_geometry is not None:
                    logger.info(f"plz_geometry type: {type(plz_geometry)}")
                    logger.info(f"plz_geometry.boundary is None: {plz_geometry.boundary is None}")
                    if plz_geometry.boundary is not None:
                        logger.info(f"plz_geometry.boundary type: {type(plz_geometry.boundary)}")
                        logger.info(f"plz_geometry.boundary shape: {plz_geometry.boundary.shape}")
                        logger.info(f"plz_geometry.boundary columns: {plz_geometry.boundary.columns.tolist()}")
                        logger.info(f"First few rows:\n{plz_geometry.boundary.head()}")
                
                if plz_geometry is not None and plz_geometry.boundary is not None:
                    try:
                        # Convert the boundary GeoDataFrame to GeoJSON format
                        # The boundary is stored as a GeoDataFrame, access its geometry
                        logger.info("Converting boundary to GeoJSON...")
                        boundary_geojson = json.loads(plz_geometry.boundary.to_json())
                        logger.info(f"GeoJSON conversion successful. Type: {type(boundary_geojson)}")
                        logger.info(f"GeoJSON keys: {boundary_geojson.keys() if isinstance(boundary_geojson, dict) else 'Not a dict'}")
                        logger.info(f"GeoJSON content (first 500 chars): {str(boundary_geojson)[:500]}")
                        
                        # Add the postal code boundary as a shaded area
                        logger.info("Adding GeoJSON to folium map...")
                        folium.GeoJson(
                            boundary_geojson,
                            name=f"Postal Code {selected_postal_code}",
                            style_function=lambda x: {
                                'fillColor': '#3186cc',
                                'color': '#0066cc',
                                'weight': 2,
                                'fillOpacity': 0.5,
                            },
                            tooltip=f"Postal Code: {selected_postal_code}",
                        ).add_to(folium_map)
                        logger.info("✓ Postal code boundary added to map successfully!")
                        streamlit.success(f"✓ Postal code {selected_postal_code} boundary rendered")
                    except Exception as boundary_error:
                        logger.error(f"Error rendering boundary: {boundary_error}", exc_info=True)
                        streamlit.error(f"Error rendering postal code boundary: {boundary_error}")
                else:
                    logger.warning(f"Cannot render boundary - plz_geometry: {plz_geometry}, boundary: {plz_geometry.boundary if plz_geometry else 'N/A'}")
                    streamlit.warning(f"No boundary data available for postal code {selected_postal_code}")
                
                # Retrieve stations for the selected postal code area
                logger.info(f"Fetching charging stations for {selected_postal_code}...")
                area = self.charging_station_service.search_by_postal_code(postal_code_obj)
                logger.info(f"Found {len(area.stations)} charging stations")
                
                # Create interactive map marker for each charging station
                for idx, station in enumerate(area.stations):
                    folium.CircleMarker(
                        location=[station.latitude, station.longitude],
                        radius=6,
                        popup=f"PLZ: {station.postal_code.value}<br>Power: {station.power_kw} kW",
                        color="darkgreen",
                        fill=True,
                        fillColor="green",
                        fillOpacity=0.8,
                    ).add_to(folium_map)
                logger.info(f"✓ Added {len(area.stations)} charging station markers to map")
            else:
                # Prevent map clutter when viewing all areas
                streamlit.info("Select a specific postal code to view charging stations on the map.")
        except Exception as e:
            # Handle and display any errors gracefully in the UI
            logger.error(f"Error loading charging stations: {e}", exc_info=True)
            streamlit.error(f"Error loading charging stations: {e}")

    def _render_map_view(self, selected_postal_code: str, layer_selection: str):
        """
        Render interactive map view with user-selected data layers.

        Creates a Folium map centered on the selected area and overlays
        the chosen visualization layer (residents or charging stations).

        Args:
            selected_postal_code (str): Postal code to center map on.
            layer_selection (str): Layer type to display ("Residents" or "All Charging Stations").
        """
        # Calculate optimal map center and zoom level for selected area
        map_center, map_zoom = self._get_map_center_and_zoom(selected_postal_code)
        folium_map = folium.Map(location=map_center, zoom_start=map_zoom)

        # Render the appropriate data layer based on user selection
        if layer_selection == "Residents":
            self._render_residents_layer(folium_map)
        elif layer_selection == "All Charging Stations":
            self._render_charging_stations_layer(folium_map, selected_postal_code)

        # Display the map in Streamlit with responsive dimensions
        folium_static(folium_map, width=1400, height=800)

    def _render_demand_analysis(self, selected_postal_code: str):
        """
        Render comprehensive demand analysis dashboard with priority assessment.

        This method implements the complete demand analysis view, providing:
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
            1. Collect population and station data for all areas
            2. Perform batch demand analysis via DemandAnalysisService
            3. Display detailed metrics for selected area (if applicable)
            4. Show high-priority areas requiring immediate attention
            5. Present complete overview with color-coded priorities
            6. Provide summary statistics
        """
        streamlit.header("📊 EV Charging Infrastructure Demand Analysis")
        streamlit.markdown("*Analyzing population density and charging station coverage*")

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
                        "station_count": postal_code_area.get_station_count(),
                    }
                )

        # Perform batch analysis
        if areas_data:
            results = self.demand_analysis_service.analyze_multiple_areas(areas_data)
            
            # Convert aggregates to dicts for DataFrame
            results = [r.to_dict() for r in results]

            # If specific postal code selected, show detailed analysis
            if selected_postal_code and selected_postal_code != "All areas":
                streamlit.subheader(f"🔍 Detailed Analysis: {selected_postal_code}")

                # Get specific analysis
                analysis = self.demand_analysis_service.get_demand_analysis(selected_postal_code)

                if analysis:
                    # Convert aggregate to dict for UI
                    analysis = analysis.to_dict()
                    
                    # Display metrics in columns
                    col1, col2, col3, col4 = streamlit.columns(4)

                    with col1:
                        streamlit.metric("Population", f"{analysis['population']:,}")

                    with col2:
                        streamlit.metric("Charging Stations", analysis["station_count"])

                    with col3:
                        priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(
                            analysis["demand_priority"], "⚪"
                        )
                        streamlit.metric("Priority", f"{priority_color} {analysis['demand_priority']}")

                    with col4:
                        streamlit.metric("Residents/Station", f"{analysis['residents_per_station']:.0f}")

                    # Coverage assessment
                    streamlit.markdown("---")
                    col_assess1, col_assess2, col_assess3 = streamlit.columns(3)

                    with col_assess1:
                        streamlit.info(f"**Coverage Assessment**\n\n{analysis['coverage_assessment']}")

                    with col_assess2:
                        streamlit.info(f"**Urgency Score**\n\n{analysis['urgency_score']:.0f}/100")

                    with col_assess3:
                        expansion_status = "✅ Yes" if analysis["needs_expansion"] else "❌ No"
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
            
            # Convert aggregates to dicts for DataFrame
            high_priority_areas = [area.to_dict() for area in high_priority_areas]

            if high_priority_areas:
                streamlit.markdown(f"**🔴 {len(high_priority_areas)} High Priority Areas Identified**")

                # Display high priority areas
                high_priority_df = pd.DataFrame(high_priority_areas)
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

                streamlit.dataframe(high_priority_df, width='stretch', hide_index=True)

            # Display overview table with color-coded priority visualization
            streamlit.markdown("---")
            streamlit.subheader("📊 All Areas Analysis")

            results_df = pd.DataFrame(results)
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
                if row['Priority'] == 'Medium':
                    return ['background-color: #ffd93d; color: black; font-weight: bold'] * len(row)
                return ['background-color: #6bcf7f; color: white; font-weight: bold'] * len(row)

            styled_df = results_df.style.apply(highlight_priority, axis=1)

            streamlit.dataframe(styled_df, width='stretch', hide_index=True)

            # Summary statistics
            streamlit.markdown("---")
            streamlit.subheader("📈 Summary Statistics")

            col_stat1, col_stat2, col_stat3 = streamlit.columns(3)

            high_count = len([r for r in results if r["demand_priority"] == "High"])
            medium_count = len([r for r in results if r["demand_priority"] == "Medium"])
            low_count = len([r for r in results if r["demand_priority"] == "Low"])

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
