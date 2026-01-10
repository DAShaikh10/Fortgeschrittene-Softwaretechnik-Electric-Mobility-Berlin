"""
About View - Shared View Component.

This view handles the display of application information and documentation.
"""

import streamlit

from docs import ABOUT_SECTION


class AboutView:
    """
    View component for displaying application information.

    Responsibilities:
    - Render application documentation
    - Display project information
    - Show usage guidelines
    """

    def __init__(self):
        """Initialize About View."""

    def render_about(self) -> None:
        """Render about/information view."""
        streamlit.header("ℹ️ About EVision Berlin")
        streamlit.markdown(ABOUT_SECTION)
