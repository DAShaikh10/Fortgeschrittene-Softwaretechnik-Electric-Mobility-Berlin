"""
About Section for EVision Berlin Application.
"""

ABOUT_SECTION = """
    ## 🚗 EVision Berlin - Electric Vehicle Charging Station Analysis

    ### Overview

    **EVision Berlin** is a comprehensive data analysis and visualization platform that helps identify gaps in
    Berlin's electric vehicle (EV) charging infrastructure. The application analyzes population density, existing
    charging station distribution, and power capacity across Berlin's postal codes to provide actionable insights
    for urban planners, policymakers, and EV infrastructure developers.

    **Live Application**: [evision-berlin.streamlit.app](https://evision-berlin.streamlit.app/)

    ---

    ### 🎯 Purpose & Target Users

    **What Problem Does It Solve?**
    - Identifies areas with high EV charging demand but insufficient infrastructure
    - Provides data-driven recommendations for charging station deployment
    - Visualizes geographic distribution of charging infrastructure vs. population density
    - Helps prioritize infrastructure investments based on demand analysis

    **Target Users:**
    - **Urban Planners**: Strategic infrastructure planning and resource allocation
    - **Policymakers**: Evidence-based decision making for sustainable transportation
    - **EV Infrastructure Developers**: Market opportunity identification and expansion planning
    - **Researchers**: Academic analysis of urban EV infrastructure patterns

    ---

    ### ✨ Key Features

    - 🗺️ **Interactive Map Visualization**: Dynamic Folium maps with postal code boundaries and station markers
    - 📊 **Population Density Analysis**: Visual heatmaps showing resident distribution across Berlin
    - ⚡ **Power Category Filtering**: Analyze stations by charging speed (Slow, Normal, Fast, Rapid, Ultra-rapid)
    - 🔍 **Postal Code Search**: Instant lookup with detailed area statistics
    - 📈 **Demand Priority Analysis**: Automated high/medium/low priority classification
    - 🎯 **Smart Recommendations**: Infrastructure expansion suggestions based on target ratios
    - 📊 **Data Quality Dashboard**: Comprehensive statistical analysis with outlier detection
    - 🔄 **Real-time Statistics**: Key metrics and demand indicators updated dynamically

    ---

    ### 🏛️ Domain-Driven Design Architecture

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

    ### 🧪 Testing Strategy (TDD Approach)

    **Test-Driven Development Practices:**
    - **Unit Tests**: Comprehensive coverage for domain logic, value objects, aggregates, and services
    - **Integration Tests**: Repository implementations, event bus, and cross-context interactions
    - **Test Coverage**: High coverage maintained across all layers (Domain, Application, Infrastructure)
    - **Continuous Testing**: Automated test execution via GitHub Actions on every commit
    - **Coverage Reporting**: HTML coverage reports generated for detailed analysis

    **Testing Tools:**
    - `pytest`: Primary testing framework
    - `pytest-cov`: Code coverage measurement
    - `unittest.mock`: Mocking and stubbing for isolated unit tests

    **Quality Assurance:**
    - `pylint`: Code quality and style enforcement
    - `black`: Automated code formatting
    - `pre-commit`: Git hooks for quality checks before commits

    ---

    ### 🛠️ Technologies & Dependencies

    **Core Technologies:**
    - **Python 3.10+**: Modern Python with type hints and dataclasses
    - **Streamlit 1.51+**: Interactive web application framework
    - **Pandas**: Data manipulation and analysis
    - **GeoPandas**: Geospatial data processing
    - **Folium**: Interactive map visualizations
    - **Matplotlib/Seaborn**: Statistical visualizations
    - **SciPy**: Statistical analysis and outlier detection

    **Development Tools:**
    - **pytest**: Testing framework
    - **pylint**: Code linting
    - **black**: Code formatting
    - **pre-commit**: Git hooks
    - **taskipy**: Task automation

    ---

    ### 📦 Installation & Setup

    **Prerequisites:**
    ```bash
    Python 3.10 or higher
    pip (Python package manager)
    ```

    **Quick Start:**
    ```bash
    # Clone the repository
    git clone https://github.com/DAShaikh10/EVision-Berlin.git
    cd EVision-Berlin

    # Install dependencies
    pip install -r requirements.txt
    # OR using task command
    task install

    # Run the application
    streamlit run main.py
    # OR using task command
    task run
    ```

    **Task Commands (using taskipy):**
    ```bash
    # Development commands
    task install         # Install all dependencies
    task run            # Run the Streamlit application
    task run-clean      # Clean cache and run application

    # Testing commands
    task test           # Run all tests with verbose output
    task test-cov       # Run tests with coverage report (HTML + terminal)

    # Code quality commands
    task format         # Format code with black
    task format-check   # Check code formatting without modifying
    task lint           # Run pylint on main.py, config.py, src/, and tests/
    task clean          # Remove all __pycache__ directories

    # Git workflow commands
    task pull-main      # Stash changes, pull from main, restore changes
    task pull-task      # Stash changes, pull from task branch, restore changes
    ```

    ---

    ### 🚀 How to Use

    1. **Access the Application**: Visit [evision-berlin.streamlit.app](https://evision-berlin.streamlit.app/)
       or run locally

    2. **Enter Postal Code**: Input a 5-digit Berlin postal code (10xxx-14xxx range)

    3. **View Analysis Results**:
       - Interactive map with charging stations and postal code boundaries
       - Population density statistics
       - Existing infrastructure count by power category
       - Demand priority classification (High/Medium/Low)
       - Recommendations for additional charging points needed

    4. **Explore Filters**:
       - Filter by power category (Slow, Normal, Fast, Rapid, Ultra-rapid)
       - View data quality analysis and outlier detection
       - Compare multiple postal codes

    5. **Interpret Recommendations**:
       - **High Priority**: Significant infrastructure gap, immediate action needed
       - **Medium Priority**: Moderate shortfall, consider expansion
       - **Low Priority**: Adequate coverage, monitor for future needs

    ---

    ### 📈 Analysis Methodology

    **Demand Calculation:**
    - Infrastructure ratio: Charging points per 1000 residents
    - Target threshold: Industry benchmarks for adequate coverage
    - Gap analysis: Difference between current and required infrastructure

    **Priority Classification:**
    - **High Priority**: Large population (>5000) + Low infrastructure ratio (<0.5 per 1000)
    - **Medium Priority**: Moderate population or moderate infrastructure shortfall
    - **Low Priority**: Small population (<2000) or adequate infrastructure coverage

    **Power Category Analysis:**
    - Slow: < 11 kW (home/workplace charging)
    - Normal: 11-22 kW (public charging)
    - Fast: 22-50 kW (semi-rapid charging)
    - Rapid: 50-150 kW (highway charging)
    - Ultra-rapid: > 150 kW (next-gen fast charging)

    ---

    ### ⚠️ Limitations

    - Data based on publicly available datasets (may not reflect real-time changes)
    - Analysis focuses on Berlin postal codes only (10xxx-14xxx range)
    - Does not account for future population growth projections
    - Private charging infrastructure (home chargers) not included
    - Assumes uniform charging demand across postal code areas

    ---

    **Version**: 2.0 (TDD Enhanced DDD) <br>
    **Framework**: Streamlit + DDD + TDD + Event-Driven Architecture <br>
    **Course**: Advanced Software Engineering <br>
    **Institution**: Berlin University of Applied Sciences (BHT) <br>
    **Professor**: Dr. Prof. Selcan Ipek Ugay

    **Development Team**:
    - [Amaan Aslam Shaikh](https://github.com/Amaan6674)
    - [Danish Ali Abdul Kareem Shaikh](https://github.com/DAShaikh10)
    - [Hrusheekesh Sawarkar](https://github.com/hrusheekeshsawarkar)
    - [Melisa Cihan](https://github.com/melisa-cihan)

    ---

    ### 📫 Contact & Contribution

    **GitHub Repository**: [DAShaikh10/EVision-Berlin](https://github.com/DAShaikh10/EVision-Berlin) <br>
    **Issues & Feedback**: [GitHub Issues](https://github.com/DAShaikh10/EVision-Berlin/issues)

    Contributions, bug reports, and feature requests are welcome!
"""
