# Data Quality Analysis & Outlier Detection

## Overview

This document describes the comprehensive data quality analysis and outlier detection functionality that has been added to the EVision-Berlin project. The analysis generates detailed visualizations and statistical summaries to identify anomalies, outliers, and data quality issues in the Berlin EV charging infrastructure dataset.

## Implementation

### New Function Added

`analyze_data_quality_and_outliers()` in `/core/methods.py`

This function performs a comprehensive analysis of:
1. **Charging Stations Data** - Power capacity, distribution, outliers
2. **Residents Data** - Population distribution, outliers, normality
3. **Combined Analysis** - Correlation between infrastructure and population

### Integration

The function has been integrated into `main.py` and runs automatically after data preprocessing and before the demand analysis.

## Output Visualizations

### 1. Charging Stations Data Quality Analysis
**File:** `data_quality_charging_stations.png`

Contains 6 subplots:
- **Distribution of Power Capacity (KW)**: Histogram showing the frequency distribution of charging station power ratings
  - Most stations are in the 11-44 kW range (Normal charging)
  - Mean and median lines indicate central tendency
  
- **Box Plot: Power Capacity Outliers**: Identifies outliers using IQR method
  - Shows 461 outliers (12.58%) with power > 77 kW
  - Range: 6-600 kW
  
- **Distribution by Power Category**: Bar chart categorizing stations by power level
  - Slow (<11 kW): ~1,500 stations
  - Normal (11-22 kW): ~550 stations
  - Fast (22-50 kW): ~300 stations
  - Rapid (50-150 kW): ~270 stations
  - Ultra (>150 kW): ~250 stations
  
- **Stations per Postal Code**: Distribution of station counts across PLZ areas
  - Average: 19.5 stations per PLZ
  - Range: 1-105 stations
  
- **Missing Data Percentage**: Shows data completeness
  - Only KW_numeric has ~22% missing values
  - All geographic data is complete
  
- **Top 10 PLZ by Station Count**: Identifies areas with highest infrastructure
  - PLZ 12683: 105 stations (highest)
  - PLZ 12623: 90 stations
  - PLZ 10117: 82 stations

### 2. Residents Data Quality Analysis
**File:** `data_quality_residents.png`

Contains 6 subplots:
- **Distribution of Population per PLZ**: Histogram of population distribution
  - Mean: 17,305 residents
  - Median: 16,865 residents
  - Range: 139 - 35,353 residents
  
- **Box Plot: Population Outliers**: Identifies population outliers
  - 2 outliers detected (1.05%)
  - PLZ 12627: 35,353 (very high)
  - PLZ 14053: 139 (very low)
  
- **Distribution by Population Category**: Population segmentation
  - High (15-20K): ~60 PLZ areas
  - Very High (>20K): ~58 PLZ areas
  - Medium (10-15K): ~51 PLZ areas
  - Low (5-10K): ~16 PLZ areas
  - Very Low (<5K): ~4 PLZ areas
  
- **Top 10 PLZ by Population**: Most populated areas
  - PLZ 12627: 35,353 residents
  - PLZ 10247: 32,718 residents
  - PLZ 12353: 31,055 residents
  
- **Missing Data Percentage**: All resident data is complete (0% missing)
  
- **Q-Q Plot: Population Normality Check**: Tests if population follows normal distribution
  - Shows slight deviation from normality at the extremes
  - Most data follows normal distribution

### 3. Combined Analysis: Infrastructure vs Population
**File:** `data_quality_combined.png`

Contains 4 subplots:
- **Population vs Charging Stations**: Scatter plot showing relationship
  - Correlation coefficient: 0.131 (weak positive correlation)
  - Indicates infrastructure deployment doesn't strongly follow population density
  - Some high-population areas have few stations (opportunity for expansion)
  
- **Distribution: Residents per Station**: Histogram of service burden
  - Mean: 1,898 residents per station
  - Median: 1,290 residents per station
  - Range: 68 - 16,381 residents per station
  
- **Correlation Heatmap**: Visual representation of variable relationships
  - Population and station count have weak correlation (0.131)
  
- **Population in PLZ without Stations**: Identifies underserved areas
  - PLZ 10115: 20,313 residents (NO stations) - Critical gap
  - PLZ 14053: 139 residents (NO stations)

## Key Findings from Analysis

### Charging Stations
- **Total Berlin Stations**: 3,664
- **Power Capacity Range**: 6.00 - 600.00 kW
- **Power Capacity Outliers**: 461 (12.58%)
  - Most outliers are ultra-rapid chargers (>150 kW)
- **Missing KW Data**: 819 records (22.4%)
- **Stations per PLZ**: Average 19.5, Range 1-105

#### Notable Insights:
- **High-capacity areas** (>50 stations): 12 PLZ identified
  - These may indicate commercial/industrial areas
- **Low-capacity areas** (<3 stations): 13 PLZ identified
  - Potential areas for infrastructure expansion

### Residents
- **Total Berlin PLZ**: 191
- **Population Range**: 139 - 35,353
- **Population Outliers**: 2 (1.05%)
  - PLZ 12627: Extremely high density (35,353)
  - PLZ 14053: Extremely low density (139)
- **Missing Data**: 0% (complete dataset)

### Infrastructure Coverage
- **Correlation (Population vs Stations)**: 0.131
  - **Finding**: Weak correlation indicates that charging station deployment is NOT primarily driven by population density
  - **Implication**: Other factors (commercial activity, parking availability, policy) may be more influential
  
- **PLZ Without Stations**: 2
  - PLZ 10115: 20,313 residents - **CRITICAL GAP**
  - PLZ 14053: 139 residents
  
- **Average Residents per Station**: 1,898

## Anomalies Detected

### 1. Power Capacity Anomalies
- **461 outlier stations** with power >77 kW
- **Maximum 600 kW** station (ultra-rapid charging)
- **819 missing KW values** need investigation

### 2. Population Anomalies
- **PLZ 12627**: 35,353 residents (outlier - very high density)
- **PLZ 14053**: 139 residents (outlier - very low density)

### 3. Infrastructure Gaps
- **PLZ 10115**: 20,313 residents with ZERO charging stations
  - This is the most critical infrastructure gap
  - High priority for new station deployment

### 4. Over-provisioned Areas
- **PLZ 12683**: 105 stations for likely commercial/industrial use
- **PLZ 12623**: 90 stations
- **PLZ 10117**: 82 stations (low population, high stations = commercial area)

### 5. Weak Population-Infrastructure Correlation (0.131)
- Suggests systematic issues in infrastructure planning
- Station placement may be driven by:
  - Commercial/industrial zones
  - Parking availability
  - Property ownership
  - Policy incentives
  - Rather than population density alone

## Statistical Methods Used

### Outlier Detection
- **IQR (Interquartile Range) Method**
  - Q1 = 25th percentile
  - Q3 = 75th percentile
  - IQR = Q3 - Q1
  - Outliers: < Q1 - 1.5×IQR or > Q3 + 1.5×IQR

### Normality Testing
- **Q-Q Plot (Quantile-Quantile)**
  - Compares data distribution to theoretical normal distribution
  - Deviations indicate non-normality

### Correlation Analysis
- **Pearson Correlation Coefficient**
  - Measures linear relationship between variables
  - Range: -1 (perfect negative) to +1 (perfect positive)
  - 0.131 = weak positive correlation

## Usage

### Running the Analysis

```python
# Automatic execution in main.py
python main.py
```

The analysis runs automatically and generates:
1. Three PNG visualization files
2. Console output with detailed statistics
3. Summary of key findings

### Programmatic Usage

```python
from core import methods as mt

# After loading and preprocessing data
mt.analyze_data_quality_and_outliers(
    df_geodat_plz=df_geodat_plz,
    df_lstat=df_lstat,
    df_residents=df_residents,
    gdf_lstat3=gdf_lstat3,        # Optional: processed station data
    gdf_residents2=gdf_residents2  # Optional: processed resident data
)
```

## Dependencies Added

- `numpy` - Numerical computations
- `scipy` - Statistical analysis (Q-Q plots)
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical data visualization

These have been added to `requirements.txt`.

## Future Enhancements

1. **Time-series Analysis**: Track infrastructure growth over time
2. **Geospatial Clustering**: Identify geographic patterns in anomalies
3. **Predictive Modeling**: Forecast optimal station placement
4. **Interactive Dashboards**: Real-time outlier monitoring
5. **Automated Alerts**: Flag new anomalies as data updates

## Recommendations Based on Analysis

### High Priority Actions
1. **Address PLZ 10115**: Deploy charging stations for 20,313 unserved residents
2. **Investigate Missing KW Data**: 819 records need power rating information
3. **Rebalance Infrastructure**: Some areas over-provisioned while others underserved

### Medium Priority Actions
1. **Study Correlation Factors**: Why is population correlation so weak (0.131)?
2. **Validate Ultra-Rapid Chargers**: Confirm 600 kW stations are correctly recorded
3. **Review Low-Station PLZ**: 13 areas with <3 stations may need expansion

### Data Quality Improvements
1. **Complete Power Ratings**: Fill in 819 missing KW values
2. **Validate Outliers**: Verify PLZ 12627 (35,353 residents) is accurate
3. **Regular Monitoring**: Set up periodic data quality checks

## Conclusion

The data quality analysis reveals:
- **Good**: High data completeness (only 22% missing KW values)
- **Concern**: Weak population-infrastructure correlation suggests planning gaps
- **Critical**: PLZ 10115 needs immediate attention (20K+ residents, zero stations)
- **Opportunity**: 461 ultra-rapid chargers show Berlin is investing in high-speed infrastructure

The visualizations provide clear evidence of where anomalies exist and help prioritize infrastructure expansion efforts.

