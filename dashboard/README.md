```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

DASHBOARD 
```

# Boreas Dashboard

Professional Streamlit dashboard for real-time visualization of avalanche danger levels and weather conditions across Norwegian regions. Features interactive maps, time-series analysis, and comprehensive data analytics.

## Core Features

| Feature Category | Description | Key Capabilities |
|------------------|-------------|------------------|
| **Interactive Mapping** | Real-time regional visualization | Color-coded danger levels, hover details, date selection |
| **Time Series Analytics** | Historical trend analysis | Date range filtering, danger level heatmaps |
| **Weather Integration** | Comprehensive meteorological data | Temperature ranges, precipitation, wind conditions |
| **Data Export** | Professional reporting tools | Tabular views, metrics dashboard, filtering |

## Quick Start

### System Requirements
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Completed data pipeline (DLT + dbt transformations)
- DuckDB database with processed avalanche/weather data

### Installation

```bash
# Install dashboard dependencies
uv sync --extra dashboard

# Verify data availability
cd dlt && uv run python run_dlt_pipelines.py
cd ../dbt_boreas && uv run dbt run

# Launch dashboard
cd ../dashboard
uv run streamlit run app.py
```

**Access Point**: `http://localhost:8501`

## Technical Architecture

### Data Pipeline Integration
- **Source**: Gold layer models from dbt transformations
- **Primary Table**: `3_gold.avalanche_average_weather_per_region`
- **Database**: DuckDB (`./boreas.duckdb`)


## Project Structure

```
dashboard/
├── app.py                 # Main Streamlit application entry point
├── README.md             # Professional documentation (this file)
└── .streamlit/
    └── config.toml       # Dashboard configuration and theming
```
