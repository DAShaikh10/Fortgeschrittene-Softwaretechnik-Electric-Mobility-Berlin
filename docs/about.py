"""
About Section for EVision Berlin Application.
"""

ABOUT_SECTION = """
    ### Domain-Driven Design Architecture

    This application is built using **Domain-Driven Design (DDD)** principles with **Test-Driven Development (TDD)**:

    #### 🎯 Bounded Contexts

    1. **Station Discovery Context**
        - **Aggregate Root**: `PostalCodeAreaAggregate` - manages charging station collections by area
        - **Entities**: `ChargingStation` - represents individual charging infrastructure
        - **Value Objects**: `PostalCode`, `GeoLocation` - immutable domain concepts
        - **Services**: `ChargingStationService`, `GeoLocationService` - use case orchestration
        - **Repositories**: `CSVChargingStationRepository`, `CSVGeoDataRepository` - data persistence

    2. **Demand Analysis Context**
        - **Aggregate Root**: `DemandAnalysisAggregate` - encapsulates demand calculations and priority
        - **Value Objects**: `DemandPriority` - priority level categorization
        - **Services**: `DemandAnalysisService` - analyzes infrastructure demand
        - **Domain Events**: `DemandAnalysisCalculatedEvent`, `HighDemandAreaIdentifiedEvent`
        - **Repositories**: `InMemoryDemandAnalysisRepository` - demand data storage

    3. **Shared Kernel**
        - **Value Objects**: `PostalCode`, `GeoLocation`, `PopulationData` - shared across contexts
        - **Domain Events**: `DomainEventBus`, `StationSearchPerformedEvent` - event-driven architecture
        - **Services**: `PostalCodeResidentService` - resident data operations
        - **Exceptions**: `InvalidPostalCodeError`, `InvalidGeoLocationError` - domain validation

    #### 🏗️ Architecture Layers

    - **Domain Layer**:
        - Business logic encapsulated in aggregates and value objects
        - Domain events for loose coupling between contexts
        - Invariant enforcement through value object validation
        - **Named Constants**: Business thresholds in dedicated constant classes (no magic numbers)
        - **Type-Safe Enums**: ChargingCategory, PopulationDensityCategory, CapacityCategory

    - **Application Layer**:
        - Service orchestration of domain operations
        - Use case implementations (search stations, analyze demand, get recommendations)
        - Cross-aggregate coordination through domain events
        - Data Transfer Objects (DTOs) for presentation layer isolation

    - **Infrastructure Layer**:
        - CSV-based repository implementations
        - Centralized logging configuration with structured logging
        - GeoDataFrame processing for geographic boundaries
        - Event bus for domain event publishing

    - **UI Layer**:
        - Streamlit-based presentation with responsive design
        - DDD validation with user-friendly error messages
        - Interactive map visualization with Folium
        - Modular rendering methods for maintainability

    #### ✅ Key Features

    - **Domain Validation**: PostalCode enforces Berlin-specific rules (10xxx-14xxx, 5 digits)
    - **Error Handling**: Domain exceptions translated to user-friendly messages
    - **Event-Driven**: Domain events track searches and high-demand area identification
    - **Geographic Visualization**: Interactive maps with postal code boundaries and station markers
    - **Priority Analysis**: Automated demand priority calculation (High/Medium/Low)
    - **Recommendations Engine**: Infrastructure expansion suggestions based on target ratios
    - **Centralized Logging**: Structured logging throughout all layers for observability
    - **Type Safety**: Enums replace magic strings for better IDE support and refactoring safety
    - **Maintainable Constants**: Business rules defined in named constants, not hardcoded values

    #### 📊 Data Sources

    - **Ladesäulenregister**: Official charging station registry from BNetzA (Federal Network Agency)
    - **PLZ Einwohner**: Berlin population data by postal code
    - **Geodata Berlin PLZ**: Geographic boundary data in WKT format for postal code areas

    #### 🔧 Technical Implementation

    - **Value Object Validation**: Immutable with invariant enforcement in `__post_init__`
    - **Aggregate Pattern**: Clear boundaries with internal consistency rules
    - **Repository Pattern**: Abstract data access with CSV implementations
    - **Service Layer**: Stateless orchestration of domain operations
    - **Domain Events**: Publisher-subscriber pattern for cross-context communication
    - **Constants Module**: Centralized business thresholds (InfrastructureThresholds, PowerThresholds, etc.)
    - **Enum Types**: Type-safe categorization for charging speeds, population density, and capacity levels
    ---

    **Version**: 2.0 (TDD Enhanced DDD)  
    **Framework**: Streamlit + DDD + TDD + Event-Driven Architecture  
    **Course**: Advanced Software Engineering  
    **Authors**:
    - [Amaan Shaikh](https://github.com/Amaan6674)
    - [Danish Ali Shaikh](https://github.com/DAShaikh10)
    - [Hrusheekesh Sawarkar](https://github.com/hrusheekeshsawarkar)
    - [Melisa Cihan](https://github.com/melisa-cihan)
"""
