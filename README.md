# EVision Berlin

## Project Description

EVision Berlin analyzes the demand for electric vehicle charging stations in Berlin by visualizing the relationship between population density and existing charging infrastructure. The application provides interactive heatmaps to identify areas that require additional charging stations based on postal code analysis.

**Course:** Advanced Software Engineering

## Team Members

1. Amaan Aslam Shaikh
2. Danish Ali Abdul Kareem Shaikh
3. Hrusheekesh Sawarkar
4. Melisa Cihan

## Key Features

- Interactive map visualization of Berlin charging stations
- Population density heatmap by postal code
- Power category filtering (Slow, Normal, Fast, Rapid, Ultra-rapid charging)
- ZIP code search functionality
- Real-time statistics dashboard
- Dual-layer visualization (Population vs Charging Infrastructure)

## Data Sources

- **Charging Station Registry:** [Bundesnetzagentur](https://www.bundesnetzagentur.de/DE/Fachthemen/ElektrizitaetundGas/E-Mobilitaet/start.html)
- **Population Data:** Berlin postal code resident statistics
- **Geographic Data:** Berlin postal code boundary shapefiles

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Amaan6674/Electric-Mobility-Berlin.git
   cd Electric-Mobility-Berlin
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run main.py
   ```

## Project Structure

```
Electric-Mobility-Berlin/
├── main.py                     # Main application
├── config.py                   # Configuration settings
├── requirements.txt            # Dependencies
├── core/                       # Core modules
│   ├── methods.py             # Data processing & visualization
│   └── helper_tools.py        # Utility functions
└── datasets/                   # Data files
    ├── Ladesaeulenregister.csv
    ├── plz_einwohner.csv
    └── geodata files
```

## Technologies Used

- **Streamlit:** Web application framework
- **Folium:** Interactive maps
- **GeoPandas:** Geographic data processing
- **Pandas:** Data manipulation
