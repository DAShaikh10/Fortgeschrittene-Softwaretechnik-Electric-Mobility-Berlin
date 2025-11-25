# EVision Berlin - Electric Vehicle Charging Station Analysis

## Project Overview

EVision Berlin analyzes the demand for electric vehicle (EV) charging stations in Berlin by visualizing:

1. **Population density** per postal code (PLZ)
2. **Existing charging station distribution** per postal code
3. **Power categories** for different charging speeds

The analysis helps identify areas with high population density but low charging station coverage, indicating potential demand for additional infrastructure. This project provides actionable insights for urban planners, policymakers, and EV infrastructure developers.

<div align="center">

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.51+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

</div>

**Course:** Advanced Software Engineering

## Team Members

1. Amaan Aslam Shaikh
2. Danish Ali Abdul Kareem Shaikh
3. Hrusheekesh Sawarkar
4. Melisa Cihan

---

## Table of Contents

1. [Key Features](#key-features)
2. [Program Structure](#program-structure)
3. [Data Sources](#data-sources)
4. [Installation & Setup](#installation--setup)
5. [How to Run](#how-to-run)
6. [Application Usage](#application-usage)
7. [Results Interpretation](#results-interpretation)
8. [Demand Analysis](#demand-analysis)
9. [Limitations of Analysis](#limitations-of-analysis)
10. [Technologies Used](#technologies-used)

---

## Key Features

- 🗺️ **Interactive Map Visualization:** Dynamic Folium maps displaying Berlin charging stations with geographic precision
- 📊 **Population Density Heatmap:** Visual representation of resident distribution by postal code
- ⚡ **Power Category Filtering:** Analyze charging stations by power output:
  - Slow (< 11 kW)
  - Normal (11-22 kW)
  - Fast (22-50 kW)
  - Rapid (50-150 kW)
  - Ultra-rapid (> 150 kW)
- 🔍 **ZIP Code Search:** Instant lookup of specific postal code areas
- 📈 **Real-time Statistics Dashboard:** Key metrics and demand indicators
- 🔄 **Dual-layer Visualization:** Simultaneous comparison of population vs. charging infrastructure
- 📋 **Demand Priority Analysis:** Automated calculation of high-demand areas

---

## Program Structure

```
EVision-Berlin/
├── main.py                          # Main entry point for the Streamlit application
├── config.py                        # Configuration file with data file paths
├── requirements.txt                 # Python package dependencies
├── README.md                        # This documentation file
├── core/                            # Core modules
│   ├── __init__.py                 # Package initializer
│   ├── methods.py                  # Core data processing and visualization functions
│   └── helper_tools.py             # Utility functions (timer, serialization, etc.)
└── datasets/                        # Data files
    ├── Ladesaeulenregister.csv     # Charging station data from Bundesnetzagentur
    ├── plz_einwohner.csv           # Population data by postal code
    ├── geodata_berlin_plz.csv      # Postal code boundary geometries (WKT format)
    ├── geodata_berlin_dis.csv      # District boundary geometries
    └── berlin_postleitzahlen/       # Shapefile data for postal codes
        ├── berlin_postleitzahlen.shp
        ├── berlin_postleitzahlen.dbf
        ├── berlin_postleitzahlen.shx
        └── berlin_postleitzahlen.prj
```

### File Descriptions

#### Core Application Files

**`main.py`**
- Entry point for the application
- Orchestrates data loading, preprocessing, and Streamlit app generation
- Executes demand analysis calculations
- Key functions:
  - `main()`: Coordinates the entire workflow from data loading to visualization

**`config.py`**
- Central configuration dictionary (`pdict`)
- Defines file paths for all datasets
- Specifies geocode column names
- Easy modification point for data sources

**`core/methods.py`**
- Contains all core data processing functions
- Key functions:
  - `load_datasets()`: Loads CSV files for geodata, charging stations, and population
  - `preprop_lstat()`: Preprocesses charging station data (filters Berlin, handles coordinates)
  - `preprop_resid()`: Preprocesses resident/population data
  - `count_plz_occurrences()`: Counts charging stations per postal code
  - `count_plz_occurrences_by_kw()`: Categorizes stations by power output
  - `calculate_demand_priority()`: Analyzes demand based on population vs. infrastructure
  - `make_streamlit_electric_charging_resid()`: Generates the complete Streamlit web interface
  - `demand_analysis_summary()`: Prints summary statistics of demand analysis

**`core/helper_tools.py`**
- Utility functions supporting the main application
- Key functions:
  - `@timer`: Decorator for measuring function execution time
  - `pickle_out()` / `pickle_in()`: Serialization for caching processed data
  - Various lambda functions for data manipulation
  - Helper functions for data cleaning and validation

---

## Data Sources

### 1. Charging Station Infrastructure (`Ladesaeulenregister.csv`)

- **Source:** Bundesnetzagentur (Federal Network Agency of Germany)
- **URL:** [https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html)
- **File Size:** ~35 MB (CSV format)
- **Total Records:** ~111,000 charging points across Germany
- **Berlin Records:** ~3,000+ charging points

**Key Columns Used:**
- `Postleitzahl`: Postal code (PLZ) - Primary geographic identifier
- `Bundesland`: Federal state (filtered to "Berlin")
- `Breitengrad`: Latitude coordinate (decimal format, comma-separated)
- `Längengrad`: Longitude coordinate (decimal format, comma-separated)
- `Nennleistung Ladeeinrichtung [kW]`: Nominal power output in kilowatts

**Data Quality Notes:**
- Coordinates use German decimal notation (comma as decimal separator)
- Application converts commas to periods for numeric processing
- PLZ range for Berlin: 10115 - 14199
- Some entries may have missing or invalid coordinates (filtered out)

### 2. Population Data (`plz_einwohner.csv`)

- **Source:** German open data portals for postal code statistics
- **Purpose:** Provides resident count per postal code
- **Records:** ~190 postal codes in Berlin

**Key Columns Used:**
- `plz`: Postal code (PLZ)
- `einwohner`: Number of residents
- `lat`: Latitude (optional, for reference)
- `lon`: Longitude (optional, for reference)

**Data Characteristics:**
- Population ranges from ~1,000 to ~40,000 residents per postal code
- Central districts typically have higher density
- Updated periodically from census data

### 3. Geographic Data (`geodata_berlin_plz.csv`)

- **Purpose:** Provides polygon geometries for postal code boundaries
- **Format:** CSV with WKT (Well-Known Text) geometry strings
- **Coordinate System:** WGS84 (EPSG:4326)

**Key Columns:**
- `PLZ`: Postal code identifier
- `geometry`: Polygon boundaries in WKT format

**Usage:**
- Enables choropleth maps (colored regions)
- Defines boundaries for each postal code area
- Allows spatial joins and geographic aggregations

### 4. District Boundaries (`geodata_berlin_dis.csv`)

- **Purpose:** Provides larger administrative district (Bezirk) boundaries
- **Format:** Similar to PLZ geodata
- **Usage:** Contextual overlays on maps

### 5. Shapefile Data (`berlin_postleitzahlen/`)

- **Alternative Format:** ESRI Shapefile format
- **Components:**
  - `.shp`: Shape geometry
  - `.dbf`: Attribute data
  - `.shx`: Shape index
  - `.prj`: Projection information
- **Usage:** Can be loaded with GeoPandas for additional analysis

---

## Installation & Setup

### Prerequisites

- **Python:** Version 3.10 or higher
- **pip:** Python package installer
- **Git:** For cloning the repository

### Step 1: Clone the Repository

```bash
git clone https://github.com/Amaan6674/Electric-Mobility-Berlin.git
cd Electric-Mobility-Berlin
```

Or download the source code ZIP and extract to a folder named `EVision-Berlin`.

### Step 2: Create Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies from your system Python installation.

**On macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

Your terminal prompt should now show `(.venv)` indicating the virtual environment is active.

### Step 3: Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

**Key Packages Installed:**

| Package | Version | Purpose |
|---------|---------|---------|
| `pandas` | Latest | Data manipulation and analysis |
| `geopandas` | Latest | Geospatial data processing |
| `streamlit` | 1.51+ | Web application framework |
| `folium` | Latest | Interactive maps |
| `streamlit-folium` | Latest | Streamlit-Folium integration |
| `branca` | Latest | Color mapping for visualizations |

### Step 4: Verify Data Files

Ensure the following files are present in the `datasets/` folder:

✅ `Ladesaeulenregister.csv` (charging stations)  
✅ `plz_einwohner.csv` (population data)  
✅ `geodata_berlin_plz.csv` (postal code boundaries)  
✅ `geodata_berlin_dis.csv` (district boundaries)

**If Missing:**
- Download `Ladesaeulenregister.csv` from [Bundesnetzagentur](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html)
- Rename to `Ladesaeulenregister.csv` if the filename includes a date
- Contact the repository maintainers for other data files

---

## How to Run

### Running Locally

1. **Activate Virtual Environment** (if not already active):
   ```bash
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```

2. **Run the Streamlit Application:**
   ```bash
   streamlit run main.py
   ```

3. **Access the Application:**
   - The app will automatically open in your default browser
   - Default URL: `http://localhost:8501`
   - If the browser doesn't open, manually navigate to the URL shown in the terminal

4. **Stop the Application:**
   - Press `Ctrl+C` in the terminal
   - Or close the terminal window

### Deploying to Streamlit Cloud

For public deployment:

1. Push your code to a GitHub repository
2. Visit [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and branch
6. Set `main.py` as the main file path
7. Click "Deploy"

**Note:** Ensure all data files are included in your repository (check file size limits).

---

## Application Usage

### Main Interface Components

#### 1. Sidebar Controls

**Power Category Filter:**
- Select one or multiple power categories
- Options: Slow, Normal, Fast, Rapid, Ultra-rapid
- Filters apply to the charging station map layer

**Postal Code Search:**
- Enter a specific Berlin postal code (10115-14199)
- Instantly zooms to and highlights the selected area
- Displays statistics for that postal code

#### 2. Statistics Dashboard

Located at the top of the main area:
- **Total Charging Stations:** Count of all stations in Berlin
- **Total Population:** Sum of residents across all postal codes
- **Average Stations per PLZ:** Mean distribution
- **Demand Ratio:** Residents per charging station (higher = more demand)

#### 3. Interactive Map

**Layers:**
- **Layer 1 - Population Density:** Colored by resident count
  - Toggle on/off via checkbox
  - Choropleth coloring (lighter to darker = fewer to more residents)
  
- **Layer 2 - Charging Stations:** Colored by station count
  - Toggle on/off via checkbox
  - Marker clusters for dense areas
  - Individual station markers

**Interactions:**
- **Zoom:** Mouse wheel or +/- buttons
- **Pan:** Click and drag
- **Click Postal Code:** View detailed statistics in popup
- **Click Marker:** View individual station information

#### 4. Demand Priority Table

Below the map:
- **High Demand Areas:** Postal codes with high population but few stations
- **Medium Demand Areas:** Balanced population-to-station ratios
- **Low Demand Areas:** Well-served areas or low population

---

## Results Interpretation

### Layer 1: Population Density per Postal Code

**Color Coding:**
- 🟡 **Yellow/Light:** Low population (< 5,000 residents)
- 🟠 **Orange:** Medium population (5,000 - 15,000 residents)
- 🔴 **Red/Dark:** High population (> 15,000 residents)

**Key Observations:**

1. **Central Districts (Mitte, Prenzlauer Berg, Friedrichshain)**
   - Darkest colors indicate highest density
   - Compact urban living with high apartment concentration
   - Young, urban demographic
   - **Expected Behavior:** High demand for public charging infrastructure

2. **Outer Districts (Pankow, Spandau, Köpenick, Marzahn-Hellersdorf)**
   - Lighter colors indicate lower density
   - More single-family homes with private parking
   - Higher likelihood of home charging installations
   - **Expected Behavior:** Lower demand for public charging

3. **Mixed-Use Areas (Kreuzberg, Neukölln, Charlottenburg)**
   - Medium-to-high population
   - Mix of residential and commercial
   - Diverse demographics
   - **Expected Behavior:** Moderate-to-high demand

**Population Distribution Insights:**
- Berlin's population centers around the inner ring (S-Bahn Ring)
- East-West divide less pronounced than historically
- Postal codes with universities/institutions may show anomalies

### Layer 2: Charging Stations per Postal Code

**Color Coding:**
- 🟡 **Yellow/Light:** Few or no stations (0-5 stations)
- 🟠 **Orange:** Moderate infrastructure (5-15 stations)
- 🔴 **Red/Dark:** Well-served areas (> 15 stations)

**Key Observations:**

1. **Business Districts & Tourist Areas**
   - Well-served despite lower resident populations
   - Examples: Potsdamer Platz, Kurfürstendamm, Alexanderplatz
   - Stations serve commuters, tourists, and commercial vehicles
   - **Insight:** Infrastructure follows economic activity, not just population

2. **Residential High-Density Areas**
   - Uneven distribution observed
   - Some high-population postal codes have minimal infrastructure
   - Historical building constraints limit installations
   - **Insight:** Old building stock creates barriers to charging station deployment

3. **Peripheral Areas**
   - Sparse coverage in outer districts
   - Long distances between stations (potential "charging deserts")
   - May rely on private home charging
   - **Insight:** Lower priority due to home charging availability

**Infrastructure Patterns:**
- Concentration along major roads and highways
- Clustering near shopping centers and parking facilities
- Gap in residential-only neighborhoods

---

## Demand Analysis

### High-Demand Areas (Critical Priority)

**Identification Criteria:**
- **Population:** RED on residents map (> 15,000 residents)
- **Infrastructure:** YELLOW on charging stations map (< 5 stations)
- **Demand Ratio:** > 5,000 residents per charging station
- **Priority:** Immediate action required

**Characteristics of High-Demand Areas:**
- Dense residential neighborhoods
- Limited existing charging infrastructure
- High apartment-to-house ratio (limited private charging)
- Growing EV adoption in the area

**Recommended Actions:**

1. **Install Fast Chargers (50+ kW)**
   - Quick turnaround for multiple users
   - Suitable for residents without home charging

2. **Target Multi-Unit Residential Buildings**
   - Partner with building management
   - Install shared charging infrastructure in parking areas

3. **Deploy Street-Side Charging**
   - Lamppost chargers (on-street parking)
   - Sidewalk-accessible stations
   - Curbside installations

4. **Create Park-and-Charge Facilities**
   - Dedicated parking with charging
   - Overnight charging options
   - Subscription-based models

**Expected Impact:**
- Reduce range anxiety for residents
- Increase EV adoption rates
- Improve air quality in dense areas

### Medium-Demand Areas (High Priority)

**Identification Criteria:**
- **Population:** ORANGE on residents map (5,000-15,000 residents)
- **Infrastructure:** YELLOW-ORANGE on charging stations map (5-15 stations)
- **Demand Ratio:** 2,000-5,000 residents per station
- **Priority:** Near-term expansion

**Characteristics:**
- Moderate population density
- Some existing infrastructure but insufficient
- Mix of residential and commercial areas
- Growing EV market penetration

**Recommended Actions:**

1. **Add Standard Level 2 Chargers (11-22 kW)**
   - Overnight/long-duration charging
   - Cost-effective installation
   - Sufficient for daily charging needs

2. **Expand Existing Station Locations**
   - Add more charge points to existing sites
   - Leverage existing electrical infrastructure
   - Reduce installation costs

3. **Partner with Retail/Parking Facilities**
   - Shopping centers (destination charging)
   - Public parking garages
   - Workplace charging programs

**Expected Impact:**
- Prevent future congestion at charging stations
- Support continued EV adoption growth
- Improve convenience for existing EV owners

### Low-Demand Areas (Future Planning)

**Identification Criteria:**
- **Population:** YELLOW-ORANGE on residents map (< 10,000 residents)
- **Infrastructure:** ORANGE-RED on charging stations map (> 10 stations)
- **Demand Ratio:** < 2,000 residents per station
- **Priority:** Monitoring and long-term planning

**Characteristics:**
- Well-served by existing infrastructure
- Lower population density
- Higher home ownership (private charging available)
- Sufficient current capacity

**Recommended Actions:**

1. **Monitor Usage Patterns**
   - Track utilization rates of existing stations
   - Identify peak usage times
   - Adjust as needed based on data

2. **Track EV Adoption Rates**
   - Watch for increases in EV registrations
   - Survey residents about future EV purchase plans
   - Anticipate future demand

3. **Plan for Long-Term Expansion**
   - Identify potential future installation sites
   - Secure permits and agreements in advance
   - Budget for phased deployment

**Expected Impact:**
- Maintain sufficient capacity as EV adoption grows
- Avoid overbuilding in low-demand areas
- Optimize infrastructure investment

### Specific Demand Indicators

The application calculates and displays:

**Demand Score Calculation:**
```
Demand Score = (Population / Number of Stations) × Density Factor
```

**Categories:**
- **Critical (Red):** Demand score > 10,000
- **High (Orange):** Demand score 5,000-10,000
- **Medium (Yellow):** Demand score 2,000-5,000
- **Low (Green):** Demand score < 2,000

---

## Limitations of Analysis

### 1. Data Limitations

**Not Included in Analysis:**

❌ **Private Charging Stations**
- Home installations (wallboxes in private garages)
- Residential building charging (private access)
- **Impact:** Actual public demand may be overestimated in areas with high home ownership

❌ **Workplace Charging**
- Office building charging facilities
- Corporate fleet charging
- **Impact:** Commuters may charge at work, reducing public demand in residential areas

❌ **Semi-Public Charging**
- Shopping center charging (may be private)
- Hotel/restaurant charging (customer-only)
- **Impact:** These reduce demand but aren't always publicly accessible

❌ **Reserved/Fleet Charging**
- Taxi and ride-sharing fleet stations
- Car-sharing service stations
- Delivery vehicle charging
- **Impact:** Stations exist but aren't available for general public

**Consequence:** True public charging demand may be higher than calculated because we cannot account for private capacity.

### 2. Housing Type Not Considered

**Issue:**
- Single-family homeowners typically install private chargers
- Apartment dwellers rely heavily on public infrastructure
- Analysis treats all residents equally

**Missing Data:**
- Ratio of apartments to single-family homes per postal code
- Percentage of residents with private parking
- Building age (affects installation feasibility)

**Impact on Analysis:**
- Demand may be **underestimated** in apartment-heavy districts
- Demand may be **overestimated** in suburban areas with high home ownership

**Mitigation Strategy:**
- Visual inspection: high-rise areas likely have higher true demand
- Cross-reference with urban planning data
- Consider historical building patterns (inner city = apartments)

### 3. Temporal Factors Not Analyzed

**Missing Considerations:**

📅 **Growth Trends**
- Population increase/decrease over time
- New residential developments
- Urban migration patterns

⚡ **EV Adoption Rates**
- Current EV penetration varies by district
- Accelerating adoption curves
- Government incentive programs

🔄 **Seasonal Variations**
- Tourist influx in summer
- Temporary residents (students)
- Business travel patterns

**Consequence:** Analysis provides a snapshot, not a predictive model.

**Recommendation:**
- Update analysis **annually** or **semi-annually**
- Track charging station installations over time
- Monitor EV registration data by postal code

### 4. Utilization vs. Availability

**Critical Distinction:**

**Availability (This Analysis):**
- Number of charging stations present
- Geographic distribution
- Total capacity

**Utilization (Not Measured):**
- How often stations are used
- Wait times and congestion
- Peak vs. off-peak usage
- Average charging duration

**Reality:**
- **10 stations at 90% utilization** = severe shortage, long wait times
- **5 stations at 20% utilization** = excess capacity, no congestion

**Ideal Enhancement:**
- Integrate **real-time usage data** from charging networks
- Calculate **occupancy rates** and **wait times**
- Identify **congestion hotspots**
- Measure **charging session duration**

**Data Sources for Future Work:**
- Charging network APIs (e.g., Charge Point, Ionity)
- Berlin municipal data on public charging usage
- User surveys and complaint data

### 5. Power Output Distribution

**Current Analysis:**
- Counts stations regardless of power output
- Optional filtering by power category

**Missing Insights:**
- One ultra-rapid charger (150+ kW) serves more users per day than multiple slow chargers
- Charging speed affects turnover and capacity
- Mismatch between supply and user needs

**Future Improvement:**
- Weight stations by throughput capacity
- Calculate "effective" station count based on power output
- Recommend optimal mix of slow/fast/rapid chargers per area

### 6. Accessibility and Availability

**Not Addressed:**
- **24/7 Availability:** Some stations have restricted hours
- **Network Membership:** Some require specific RFID cards/apps
- **Pricing Tiers:** Cost variation affects usage patterns
- **Physical Accessibility:** Parking availability, wheelchair access

### 7. Competing Infrastructure

**Not Considered:**
- Proximity to neighboring postal codes with good infrastructure
- Residents may drive short distances to nearby areas
- Edge effects at postal code boundaries

**Impact:** Demand at borders may be shared between adjacent areas.

---

## Technologies Used

### Core Frameworks

| Technology | Purpose | Key Features Used |
|------------|---------|-------------------|
| **Python 3.10+** | Programming language | Type hints, dataclasses, f-strings |
| **Streamlit** | Web application framework | Interactive widgets, caching, layout |
| **Folium** | Interactive mapping | Choropleth maps, markers, popups |
| **Pandas** | Data manipulation | DataFrames, groupby, merge |
| **GeoPandas** | Geospatial data | GeoDataFrames, spatial joins, WKT parsing |

### Supporting Libraries

| Library | Purpose |
|---------|---------|
| **Branca** | Color mapping for visualizations |
| **Streamlit-Folium** | Integration between Streamlit and Folium |
| **Pickle** | Data serialization and caching |

### Development Tools

- **Git:** Version control
- **pip:** Package management
- **Virtual Environment:** Dependency isolation

---

## Future Enhancements

### Planned Features

1. **Separate Layers for Each Power Category**
   - Individual map layers for Slow, Normal, Fast, Rapid, Ultra-rapid
   - Toggle each category independently
   - Analyze power availability distribution

2. **Data Quality Validation**
   - Automated checks for data integrity
   - Column format validation
   - Value range verification
   - Distribution analysis
   - Missing data reporting

3. **Predictive Modeling**
   - Forecast future demand based on trends
   - EV adoption rate projections
   - Population growth modeling

4. **Real-Time Data Integration**
   - Live charging station availability
   - Real-time occupancy rates
   - Wait time estimates

5. **User Feedback System**
   - Report missing stations
   - Suggest new locations
   - Rate existing infrastructure

---

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- **Bundesnetzagentur** for providing comprehensive charging station data
- **Berlin Open Data Portal** for geographic and demographic datasets
- **Streamlit Community** for excellent documentation and support
- **Course Instructors** for guidance and project requirements

---

**Last Updated:** November 2025
