"""
Shared Views - Components and utilities for UI layer.

This module provides reusable UI components and utilities shared across bounded contexts.
"""

from src.shared.views.about_view import AboutView
from src.shared.views.components import (
    get_map_center_and_zoom,
    validate_plz_input,
    render_sidebar,
)

__all__ = ["AboutView", "get_map_center_and_zoom", "render_sidebar", "validate_plz_input"]
