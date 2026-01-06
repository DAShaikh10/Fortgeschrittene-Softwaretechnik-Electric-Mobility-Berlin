"""
InvalidGeoLocationException module.
"""


class InvalidGeoLocationError(ValueError):
    """
    Raised when geo location validation fails.

    This exception is raised when:
    - Boundary data is None or empty
    - Invalid WKT format is provided
    - GeoDataFrame creation fails

    Args:
        message: Description of the validation failure
    """

    def __init__(self, message: str = "Invalid geo location data"):
        """
        Initialize InvalidGeoLocationError.
        """

        self.message = message
        super().__init__(self.message)
