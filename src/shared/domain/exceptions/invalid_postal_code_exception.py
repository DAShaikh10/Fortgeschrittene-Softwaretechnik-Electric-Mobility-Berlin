"""
InvalidPostalCodeException Module.
"""


class InvalidPostalCodeError(ValueError):
    """
    Raised when postal code validation fails.

    This exception is raised when:
    - Postal code is None or empty
    - Postal code format is invalid
    - Postal code contains non-numeric characters

    Args:
        message: Description of the validation failure
    """

    def __init__(self, message: str = "Invalid postal code"):
        """
        Initialize InvalidPostalCodeError.
        """
        self.message = message
        super().__init__(self.message)
