"""
Power Capacity View - Discovery Bounded Context.

This view handles visualization of charging station power capacity,
following DDD principles by keeping capacity-related UI concerns within Discovery.
"""

import json
import folium
import streamlit

from src.shared.infrastructure import get_logger
from src.shared.domain.value_objects import PostalCode
from src.shared.application.services import (
    GeoLocationService,
    PostalCodeResidentService,
    PowerCapacityService,
)

logger = get_logger(__name__)


class PowerCapacityView:
    """
    View component for Power Capacity visualization.

    Responsibilities:
    - Render power capacity heat maps
    - Display capacity categories (Low, Medium, High)
    - Visualize capacity distribution across postal codes
    """

    def __init__(
        self,
        power_capacity_service: PowerCapacityService,
        geolocation_service: GeoLocationService,
        postal_code_residents_service: PostalCodeResidentService,
    ):
        """
        Initialize Power Capacity View.

        Args:
            power_capacity_service: Service for power capacity analysis.
            geolocation_service: Service for geolocation data.
            postal_code_residents_service: Service for postal code resident data.
        """
        self.power_capacity_service = power_capacity_service
        self.geolocation_service = geolocation_service
        self.postal_code_residents_service = postal_code_residents_service

    def render_power_capacity_layer(
        self, folium_map: folium.Map, selected_postal_code: str, capacity_filter: str = "All"
    ):
        """
        Render power capacity visualization on the map.

        Args:
            folium_map: The Folium map object to add layers to.
            selected_postal_code: The selected postal code or "All areas".
            capacity_filter: Filter by capacity category ('All', 'Low', 'Medium', 'High').
        """
        try:
            # Get all postal codes
            postal_codes = self.postal_code_residents_service.get_all_postal_codes(sort=True)

            # Calculate power capacity for all postal codes
            capacity_dtos = self.power_capacity_service.get_power_capacity_by_postal_code(postal_codes)

            # Classify capacity ranges
            range_definitions, capacity_dtos = self.power_capacity_service.classify_capacity_ranges(capacity_dtos)

            # Apply capacity filter
            if capacity_filter != "All":
                capacity_dtos = self.power_capacity_service.filter_by_capacity_category(capacity_dtos, capacity_filter)

            if not capacity_dtos:
                streamlit.warning(f"No postal codes found in the '{capacity_filter}' capacity range.")
                return

            max_capacity = max(dto.total_capacity_kw for dto in capacity_dtos) if capacity_dtos else 0.0

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
                self._render_specific_area_capacity(folium_map, selected_postal_code, capacity_dtos, max_capacity)
            else:
                self._render_all_areas_capacity(folium_map, capacity_dtos, max_capacity)

        except Exception as e:
            logger.error("Error rendering power capacity layer: %s", e, exc_info=True)
            streamlit.error(f"Error rendering power capacity layer: {e}")

    def _render_specific_area_capacity(
        self, folium_map: folium.Map, selected_postal_code: str, capacity_dtos: list, max_capacity: float
    ):
        """Render specific postal code with capacity data."""
        postal_code_obj = PostalCode(selected_postal_code)
        plz_geometry = self.geolocation_service.get_geolocation_data_for_postal_code(postal_code_obj)

        plz_capacity_list = [dto for dto in capacity_dtos if dto.postal_code == selected_postal_code]

        if plz_geometry is not None and plz_geometry.boundary is not None and plz_capacity_list:
            plz_capacity = plz_capacity_list[0]
            capacity_value = plz_capacity.total_capacity_kw
            station_count = plz_capacity.station_count
            capacity_category = plz_capacity.capacity_category

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
                    f"Category: {capacity_category or 'N/A'}"
                ),
            ).add_to(folium_map)
        else:
            streamlit.warning(f"No capacity data available for postal code {selected_postal_code}")

    def _render_all_areas_capacity(self, folium_map: folium.Map, capacity_dtos: list, max_capacity: float):
        """Render all postal code areas with capacity data."""
        areas_rendered = 0
        for dto in capacity_dtos:
            plz = dto.postal_code
            capacity = dto.total_capacity_kw
            station_count = dto.station_count
            category = dto.capacity_category

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
                            f"Category: {category or 'N/A'}"
                        ),
                    ).add_to(folium_map)
                    areas_rendered += 1
                except Exception as e:
                    logger.warning("Could not render postal code %s: %s", plz, e)
