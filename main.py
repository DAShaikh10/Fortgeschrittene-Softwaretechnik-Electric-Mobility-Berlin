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
from src.shared.application.services import (
    ChargingStationService,
    GeoLocationService,
    PostalCodeResidentService,
    PowerCapacityService
)
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
    # Determine the current working directory.
    cwd = Path(os.getcwd())
    dataset_folder: str | None = cwd / pdict["dataset_folder"]

    # Initialize repositories with data.
    charging_station_repo = CSVChargingStationRepository(
        os.path.join(dataset_folder, pdict["file_lstations"])
    )
    geo_data_repo = CSVGeoDataRepository(os.path.join(dataset_folder, pdict["file_geodat_plz"]))
    population_repo = CSVPopulationRepository(
        os.path.join(dataset_folder, pdict["file_residents"])
    )
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
    Returns:
        Tuple of (postal_code_residents_service, charging_station_service,
        geolocation_service, demand_analysis_service, power_capacity_service)
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

    return (
        postal_code_residents_service,
        charging_station_service,
        geolocation_service,
        demand_analysis_service,
        power_capacity_service,
    )


def setup_event_handlers(event_bus: DomainEventBus):
    """
    Setup event handlers for domain events.
    """
    # Subscribe handlers.
    event_bus.subscribe(StationSearchPerformedEvent, StationSearchPerformedEvent.log_station_search)
    event_bus.subscribe(DemandAnalysisCalculatedEvent, DemandAnalysisCalculatedEvent.log_demand_calculation)
    event_bus.subscribe(HighDemandAreaIdentifiedEvent, HighDemandAreaIdentifiedEvent.log_high_demand_area)


def main():
    """
    Main: Prepares EVision Berlin Streamlit Application.
    """
    # Setup logging configuration.
    setup_logging()

    logger.info("=" * 80)
    logger.info("Preparing EVision Berlin Application ...")
    logger.info("=" * 80)

    # Initialize Domain Event Bus.
    event_bus = DomainEventBus()

    try:
        # 1. Setup repositories.
        logger.info("\n[1/4] Setting up repositories...")
        charging_station_repo, geo_data_repo, population_repo, demand_analysis_repo = setup_repositories()

        # 2. Setup services.
        logger.info("[2/4] Setting up application services...")
        (
            postal_code_residents_service,
            charging_station_service,
            geolocation_service,
            demand_analysis_service,
            power_capacity_service,
        ) = setup_services(
            charging_station_repo, geo_data_repo, population_repo, demand_analysis_repo, event_bus
        )

        # 3. Configure event handlers.
        logger.info("[3/4] Configuring event handlers...")
        setup_event_handlers(event_bus)

        # 4. Prepare Validation Data (Source of Truth)
        # Furthermore, we retrieve the authoritative list of valid Berlin PLZs from the
        # geolocation service to ensure the UI validation matches the underlying data.
        # Note: Ensure `get_all_plzs()` is implemented in your GeoLocationService.
        valid_berlin_plzs = geolocation_service.get_all_plzs()
        logger.info(
            "Loaded %d valid postal codes for validation.", len(valid_berlin_plzs)
        )

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
            valid_plzs=valid_berlin_plzs  # <--- NEW: Inject the validation list here
        )
        app.run()

    except Exception as exception:
        logger.error("An error occurred during application setup: %s", exception, exc_info=True)


if __name__ == "__main__":
    main()
