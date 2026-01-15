# Boreas Dashboard

Interactive Streamlit dashboard for visualizing avalanche danger and weather data from Norwegian regions.

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Completed data pipeline (DLT + dbt)
- DuckDB database with processed data

### Installation & Setup

1. **Install dashboard dependencies**:
```bash
uv sync --extra dashboard
```

2. **Ensure data is available**:
   - Run the DLT pipelines: `cd dlt && uv run python run_dlt_pipelines.py`
   - Run dbt transformations: `cd dbt_boreas && uv run dbt run`

3. **Launch the dashboard**:
```bash
cd dashboard
uv run streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Features

### Interactive Map
- **Regional Visualization**: Color-coded squares showing avalanche danger levels
- **Hover Details**: Temperature, wind speed, and danger information
- **Date Selection**: View data for specific dates

### Danger Level Heatmap
- **Time Series View**: Track danger levels across regions over time
- **Date Range Filtering**: Analyze trends over custom periods
- **Color Coding**: Green (low danger) to red (high danger)

### Data Analytics
- **Key Metrics**: Average danger level, temperature, precipitation, wind speed
- **Filtering**: By region, danger level, and date range
- **Data Export**: View recent data in tabular format

### Weather Integration
- **Temperature Ranges**: Min/max temperature display
- **Precipitation Data**: Rainfall and snowfall information
- **Wind Conditions**: Speed and weather type indicators

## Data Sources

The dashboard reads from the gold layer models:
- **Primary**: `3_gold.avalanche_average_weather_per_region`
- **Database**: `./boreas.duckdb` (DuckDB)

## Configuration

### Streamlit Settings
Configuration is managed in `.streamlit/config.toml`:
- Page layout and theming
- Caching settings
- Performance optimizations

### Database Connection
- **Path**: `./boreas.duckdb` (relative to dashboard directory)
- **Mode**: Read-only for dashboard safety
- **Caching**: 5-minute cache for data queries, 1-hour cache for coordinates

## Usage Tips

### Navigation
1. **Filters Panel**: Use the sidebar to customize data views
2. **Map Interaction**: Click and hover on regional squares for details
3. **Date Controls**: Separate date pickers for map and heatmap views
4. **Auto-refresh**: Data updates automatically based on filter changes


## File Structure

```
dashboard/
├── app.py              # Main Streamlit application
├── README.md           # This documentation
└── .streamlit/
    └── config.toml     # Streamlit configuration
```
