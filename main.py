"""
EVision Berlin - Main Application Entry Point

This module initializes and runs the EVision Berlin Streamlit application
for analyzing electric vehicle charging infrastructure in Berlin.
"""

import os

from pathlib import Path

from config import pdict  # Serves as the project configuration dictionary.
from src.shared.infrastructure.logging_config import get_logger, setup_logging

from src.ui.application import StreamlitApp
from src.shared.domain.events import DomainEventBus, StationSearchPerformedEvent
from src.shared.infrastructure.repositories import (
    CSVChargingStationRepository,
    CSVGeoDataRepository,
    CSVPopulationRepository,
)
from src.shared.application.services import ChargingStationService, GeoLocationService, PostalCodeResidentService, PowerCapacityService
from src.demand.application.services import DemandAnalysisService
from src.demand.domain.events import DemandAnalysisCalculatedEvent, HighDemandAreaIdentifiedEvent
from src.demand.infrastructure.repositories import InMemoryDemandAnalysisRepository

logger = get_logger(__name__)


def setup_repositories():
    """
    Setup all repository instances.

    Returns:
        Tuple of (charging_station_repo, geo_data_repo, population_repo, demand_analysis_repo)
    """

    # Determine the current working directory so that the rest of the code can use relative paths correctly.
    cwd = Path(os.getcwd())
    dataset_folder: str | None = cwd / pdict["dataset_folder"]

    # Initialize repositories with data.
    charging_station_repo = CSVChargingStationRepository(os.path.join(dataset_folder, pdict["file_lstations"]))
    geo_data_repo = CSVGeoDataRepository(os.path.join(dataset_folder, pdict["file_geodat_plz"]))
    population_repo = CSVPopulationRepository(os.path.join(dataset_folder, pdict["file_residents"]))
    demand_analysis_repo = InMemoryDemandAnalysisRepository()

    return charging_station_repo, geo_data_repo, population_repo, demand_analysis_repo


def setup_services(
    charging_station_repo: CSVChargingStationRepository,
    geo_data_repo: CSVGeoDataRepository,
    population_repo: CSVPopulationRepository,
    demand_analysis_repo: InMemoryDemandAnalysisRepository,
    event_bus: DomainEventBus,
):
    """
    Setup all application services.

    Args:
        charging_station_repo: Repository for charging stations.
        geo_data_repo: Repository for geographic data.
        population_repo: Repository for population data.
        demand_analysis_repo: Repository for demand analyses.
        event_bus: Domain event bus.

    Returns:
        Tuple of (postal_code_residents_service, charging_station_service, geolocation_service, demand_analysis_service, power_capacity_service)
    """
    # Station Discovery service.
    charging_station_service = ChargingStationService(repository=charging_station_repo, event_bus=event_bus)

    # Postal Code Residents service.
    postal_code_residents_service = PostalCodeResidentService(repository=population_repo, event_bus=event_bus)

    # Geo Location service.
    geolocation_service = GeoLocationService(repository=geo_data_repo, event_bus=event_bus)

    # Demand Analysis service.
    demand_analysis_service = DemandAnalysisService(
        repository=demand_analysis_repo,
        event_bus=event_bus,
    )

    # Power Capacity service.
    power_capacity_service = PowerCapacityService(charging_station_repository=charging_station_repo)

    return postal_code_residents_service, charging_station_service, geolocation_service, demand_analysis_service, power_capacity_service


def setup_event_handlers(event_bus: DomainEventBus):
    """
    Setup event handlers for domain events.

    Args:
        event_bus: Domain event bus to register handlers with.
    """

    # Subscribe handlers.
    event_bus.subscribe(StationSearchPerformedEvent, StationSearchPerformedEvent.log_station_search)
    event_bus.subscribe(DemandAnalysisCalculatedEvent, DemandAnalysisCalculatedEvent.log_demand_calculation)
    event_bus.subscribe(HighDemandAreaIdentifiedEvent, HighDemandAreaIdentifiedEvent.log_high_demand_area)


def main():
    """
    Main: Prepares EVision Berlin Streamlit Application for visualizing electric charging stations
    & residents in Berlin with power categories and search functionality.

    This function orchestrates the application using the DDD / TDD architecture:
    1. Sets up infrastructure. (repositories)
    2. Sets up application services.
    3. Configures event bus and handlers.
    4. Launches the Streamlit UI.
    """

    # Setup logging configuration.
    setup_logging()

    logger.info("=" * 80)
    logger.info("Preparing EVision Berlin Application ...")
    logger.info("=" * 80)

    # Initialize Domain Event Bus.
    event_bus = DomainEventBus()

    try:
        # Setup repositories.
        logger.info("\n[1/4] Setting up repositories...")
        charging_station_repo, geo_data_repo, population_repo, demand_analysis_repo = setup_repositories()

        # Setup services.
        logger.info("[2/4] Setting up application services...")
        postal_code_residents_service, charging_station_service, geolocation_service, demand_analysis_service, power_capacity_service = (
            setup_services(charging_station_repo, geo_data_repo, population_repo, demand_analysis_repo, event_bus)
        )

        # Set up event handlers
        logger.info("[3/4] Configuring event handlers...")
        setup_event_handlers(event_bus)

        logger.info("EVision Berlin Application Preparation Complete!")

        # Launch Streamlit UI.
        logger.info("\n[LAUNCH] Starting EVision Berlin Streamlit application...")
        logger.info("=" * 80)

        app = StreamlitApp(
            postal_code_residents_service=postal_code_residents_service,
            charging_station_service=charging_station_service,
            geolocation_service=geolocation_service,
            demand_analysis_service=demand_analysis_service,
            power_capacity_service=power_capacity_service,
            event_bus=event_bus,
        )
        app.run()

    except Exception as exception:
        logger.error("An error occurred during application setup: %s", exception, exc_info=True)


if __name__ == "__main__":
    main()
