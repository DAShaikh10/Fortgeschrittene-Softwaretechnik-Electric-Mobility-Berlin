"""
Shared Application Base Service
"""


class BaseService:
    """
    Base Service class for Application Services.
    """

    def __init__(self, repository):
        self.repository = repository
