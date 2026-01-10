"""
Demand Analysis View - Demand Bounded Context.

This view handles visualization of EV charging infrastructure demand analysis,
following DDD principles by keeping demand-related UI concerns within the Demand context.
"""

import json
import folium
import streamlit
import pandas as pd

from streamlit_folium import folium_static

from src.shared.infrastructure import get_logger
from src.shared.domain.value_objects import PostalCode
from src.shared.application.services import (
    ChargingStationService,
    GeoLocationService,
    PostalCodeResidentService,
)
from src.demand.application.services import DemandAnalysisService
from src.shared.views.components import get_map_center_and_zoom

logger = get_logger(__name__)


class DemandAnalysisView:
    """
    View component for Demand Analysis visualization.

    Responsibilities:
    - Render demand priority maps
    - Display demand metrics and recommendations
    - Show high-priority areas
    - Present comprehensive demand analysis tables
    """

    def __init__(
        self,
        demand_analysis_service: DemandAnalysisService,
        charging_station_service: ChargingStationService,
        geolocation_service: GeoLocationService,
        postal_code_residents_service: PostalCodeResidentService,
    ):
        """
        Initialize Demand Analysis View.

        Args:
            demand_analysis_service: Service for demand analysis operations.
            charging_station_service: Service for charging station operations.
            geolocation_service: Service for geolocation data.
            postal_code_residents_service: Service for postal code resident data.
        """
        self.demand_analysis_service = demand_analysis_service
        self.charging_station_service = charging_station_service
        self.geolocation_service = geolocation_service
        self.postal_code_residents_service = postal_code_residents_service

    def render_demand_analysis(self, selected_postal_code: str):  # pylint: disable=too-many-locals
        """
        Render comprehensive demand analysis dashboard.

        Args:
            selected_postal_code: The postal code selected for detailed analysis.
        """
        streamlit.header("📊 EV Charging Infrastructure Demand Analysis")
        streamlit.markdown("*Analyzing population density and charging station coverage*")

        # Render demand priority map
        streamlit.subheader("🗺️ Demand Priority Map")

        # Display legend
        col1, col2, col3 = streamlit.columns([2, 2, 2])
        with col1:
            streamlit.markdown("🔴 **High Priority** - >5000 residents/station")
        with col2:
            streamlit.markdown("🟡 **Medium Priority** - 2000-5000 residents/station")
        with col3:
            streamlit.markdown("🟢 **Low Priority** - <2000 residents/station")

        # Create and render demand map
        center, zoom = get_map_center_and_zoom(
            selected_postal_code, self.geolocation_service, default_center=[52.52, 13.40], default_zoom=10
        )
        demand_map = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")

        self._render_demand_map(demand_map, selected_postal_code)

        folium_static(demand_map, width=1400, height=600)

        # Get all postal codes for analysis
        postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

        # Collect data for demand analysis
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

            # Show detailed analysis for specific postal code
            if selected_postal_code and selected_postal_code != "All areas":
                self._render_detailed_analysis(selected_postal_code)

            # Show overview table
            self._render_overview_tables(analyses)
        else:
            streamlit.warning("No data available for demand analysis.")

    def _render_demand_map(self, folium_map: folium.Map, selected_postal_code: str):  # pylint: disable=too-many-locals
        """
        Render demand analysis map with color-coded priority levels.

        Args:
            folium_map: The Folium map object to add the visualization to.
            selected_postal_code: Currently selected postal code for highlighting.
        """
        try:
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
                "High": "#ff6b6b",
                "Medium": "#ffd93d",
                "Low": "#6bcf7f",
            }

            areas_rendered = 0

            # Render each postal code area with color-coded priority
            for analysis in results:
                try:
                    plz = analysis.postal_code
                    priority = analysis.demand_priority
                    postal_code_obj = PostalCode(plz)

                    plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

                    if plz_geometry is not None and plz_geometry.boundary is not None:
                        fill_color = priority_colors.get(priority, "#cccccc")

                        border_color = "#000000" if plz == selected_postal_code else "#666666"
                        border_weight = 3 if plz == selected_postal_code else 1

                        boundary_geojson = json.loads(plz_geometry.boundary.to_json())

                        urgency_score = analysis.urgency_score
                        residents_per_station = analysis.residents_per_station

                        tooltip_html = (
                            f"<b>Postal Code: {plz}</b><br>"
                            f"Priority: {priority}<br>"
                            f"Population: {analysis.population:,}<br>"
                            f"Stations: {analysis.station_count}<br>"
                            f"Residents/Station: {residents_per_station:.0f}<br>"
                            f"Urgency Score: {urgency_score:.0f}/100"
                        )

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

        except Exception as e:
            logger.error("Error rendering demand analysis map: %s", e, exc_info=True)
            streamlit.error(f"Error rendering demand analysis map: {e}")

    def _render_detailed_analysis(self, selected_postal_code: str):
        """Render detailed analysis for a specific postal code."""
        streamlit.subheader(f"🔍 Detailed Analysis: {selected_postal_code}")

        analysis = self.demand_analysis_service.get_demand_analysis(selected_postal_code)

        if analysis:
            # Display metrics
            col1, col2, col3, col4 = streamlit.columns(4)

            with col1:
                streamlit.metric("Population", f"{analysis.population:,}")

            with col2:
                streamlit.metric("Charging Stations", analysis.station_count)

            with col3:
                priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(analysis.demand_priority, "⚪")
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

    def _render_overview_tables(self, analyses: list):  # pylint: disable=too-many-locals
        """Render overview tables with all analyses."""
        streamlit.markdown("---")
        streamlit.subheader("📋 Overview: All Postal Code Areas")

        # Get high priority areas
        high_priority_areas = self.demand_analysis_service.get_high_priority_areas()
        high_priority_dicts = [area.to_dict() for area in high_priority_areas]

        if high_priority_dicts:
            streamlit.markdown(f"**🔴 {len(high_priority_dicts)} High Priority Areas Identified**")

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

        # Sort by priority level
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        results_df["priority_rank"] = results_df["Priority"].map(priority_order)
        results_df = results_df.sort_values(["priority_rank", "Residents/Station"], ascending=[True, False])
        results_df = results_df.drop("priority_rank", axis=1)

        # Apply color scheme
        def highlight_priority(row):
            """Apply color-coded styling based on demand priority."""
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
