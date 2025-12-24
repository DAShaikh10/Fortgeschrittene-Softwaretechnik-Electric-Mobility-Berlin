"""
Demand Analysis In-Memory Repository Module.
"""

from .DemandAnalysisRepository import DemandAnalysisRepository


class InMemoryDemandAnalysisRepository(DemandAnalysisRepository):
    """
    In Memory implementation of DemandAnalysisRepository.
    Stores demand analysis data in memory for quick access during runtime.
    """

    def __init__(self):
        pass
