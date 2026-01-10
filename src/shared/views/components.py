"""
Shared UI Components and Utilities.

This module provides reusable UI components and helper functions
that are used across different bounded contexts.
"""

import streamlit

from src.shared.domain.value_objects import GeoLocation, PostalCode
from src.shared.application.services import GeoLocationService


def validate_plz_input(plz_input: str, valid_plzs: list[int]) -> tuple[bool, str]:
    """
    Validate a postal code input string against Berlin requirements.

    Args:
        plz_input: The raw input string from the user.
        valid_plzs: List of valid Berlin postal codes.

    Returns:
        tuple[bool, str]: A tuple containing (is_valid, error_message).
    """
    # Handle empty input (All areas)
    if not plz_input:
        return True, ""

    # Check format: Digits only
    if not plz_input.isdigit():
        return False, "⚠️ Invalid Format: Input must contain only digits."

    # Check format: Length
    if len(plz_input) != 5:
        return False, "⚠️ Invalid Format: Postal code must be exactly 5 digits."

    # Check domain validity
    plz_int = int(plz_input)
    if plz_int not in valid_plzs:
        return False, f"⚠️ Out of Scope: PLZ {plz_input} is not within the Berlin area."

    return True, ""


def get_map_center_and_zoom(
    selected_postal_code: str,
    geolocation_service: GeoLocationService,
    default_center: list[float] | None = None,
    default_zoom: int = 10,
) -> tuple[list[float], int]:
    """
    Calculate map center and zoom level based on selected postal code.

    Args:
        selected_postal_code: The postal code to center on.
        geolocation_service: Service for geolocation data.
        default_center: Default center coordinates [lat, lon].
        default_zoom: Default zoom level.

    Returns:
        tuple: (center_coordinates, zoom_level)
    """
    if default_center is None:
        default_center = [52.52, 13.40]

    if selected_postal_code in ("", "All areas"):
        return default_center, default_zoom

    plz_geometry: GeoLocation = geolocation_service.get_geolocation_data_for_postal_code(
        PostalCode(selected_postal_code)
    )
    if plz_geometry is not None and not plz_geometry.empty:
        centroid = plz_geometry.boundary.geometry.iloc[0].centroid
        return [centroid.y, centroid.x], 13

    return default_center, default_zoom


def render_sidebar(  # pylint: disable=too-many-locals
    postal_code_residents_service,
    charging_station_service,
    valid_plzs: list[int],
) -> tuple[str, str, str, str]:
    """
    Render sidebar with search and filter options.

    Args:
        postal_code_residents_service: Service for postal code resident operations.
        charging_station_service: Service for charging station operations.
        valid_plzs: List of valid Berlin postal codes.

    Returns:
        tuple: (selected_plz, view_mode, layer_selection, capacity_filter)
    """
    streamlit.sidebar.header("🔍 View Options")

    # Postal code search
    streamlit.sidebar.markdown("---")
    streamlit.sidebar.subheader("📍 Search by Postal Code")

    plz_input = streamlit.sidebar.text_input(
        "Enter Postal Code:",
        key="postal_code_input",
        help="Enter a 5-digit Berlin Postal Code (e.g., 10117) or leave empty for all areas.",
    )

    # Perform Validation
    is_valid, error_msg = validate_plz_input(plz_input, valid_plzs)

    selected_plz = "All areas"

    if not is_valid:
        streamlit.sidebar.error(error_msg)
    else:
        if plz_input:
            selected_plz = plz_input

        # Store in session state
        streamlit.session_state["selected_plz"] = selected_plz

        if selected_plz != "All areas":
            postal_code_obj = PostalCode(selected_plz)
            postal_code_area = charging_station_service.search_by_postal_code(postal_code_obj)
            resident_data = postal_code_residents_service.get_resident_data(postal_code_obj)

            if postal_code_area and resident_data:
                info_parts = []
                info_parts.append(f"👥 Pop: {resident_data.get_population():,}")
                info_parts.append(f"⚡ Stations: {postal_code_area.station_count}")
                streamlit.sidebar.info("\n\n".join(info_parts))
            else:
                streamlit.sidebar.warning(f"PLZ {selected_plz} is valid, but no data available.")

    # Visualization mode
    streamlit.sidebar.markdown("---")
    view_mode = streamlit.sidebar.radio("Visualization Mode", ["Basic View", "Power Capacity (KW) View"])

    previous_view_mode = streamlit.session_state.get("view_mode", "Basic View")
    view_mode_changed = previous_view_mode != view_mode

    streamlit.session_state["view_mode"] = view_mode

    capacity_filter = "All"

    if view_mode == "Basic View":
        layer_options = ["Residents", "All Charging Stations"]
        if view_mode_changed:
            streamlit.session_state["layer_selection"] = "All Charging Stations"
    else:
        layer_options = ["Power Capacity"]
        if view_mode_changed:
            streamlit.session_state["layer_selection"] = "Power Capacity"

        # Add capacity range filter
        streamlit.sidebar.markdown("---")
        streamlit.sidebar.subheader("⚡ Capacity Range Filter")

        capacity_filter = streamlit.sidebar.radio(
            "Filter by Capacity:",
            ["All", "Low", "Medium", "High"],
            help="Filter postal codes by their total charging power capacity",
        )
        streamlit.session_state["capacity_filter"] = capacity_filter

    streamlit.sidebar.header("📊 Layer Selection")

    current_layer = streamlit.session_state.get("layer_selection", layer_options[0])

    if current_layer not in layer_options:
        current_layer = layer_options[0]
        streamlit.session_state["layer_selection"] = current_layer

    # Use a unique key for the radio button to prevent state conflicts
    layer_selection = streamlit.sidebar.radio(
        "Select Layer", layer_options, index=layer_options.index(current_layer), key=f"layer_radio_{view_mode}"
    )

    # Only update session state if the selection actually changed
    if layer_selection != streamlit.session_state.get("layer_selection"):
        streamlit.session_state["layer_selection"] = layer_selection

    return selected_plz, view_mode, layer_selection, capacity_filter
