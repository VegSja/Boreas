# Boreas Weather Dashboard

Interactive Streamlit dashboard for visualizing weather data from Norwegian avalanche regions.

## Setup

1. Install dashboard dependencies:
```bash
uv sync --extra dashboard
```

2. Run the dashboard:
```bash
uv run streamlit run dashboard/app.py
```

## Features

- **Interactive Map**: View current weather conditions across all regions
- **Time Series Charts**: Track temperature and precipitation trends over time
- **Filters**: Select specific regions, weather types, and date ranges
- **Real-time Metrics**: Key weather statistics at a glance

## Data Source

The dashboard connects to the duckdb database (`./boreas.duckdb`) and reads from the `2_silver.fact_weather` table.

## Navigation

- Use the sidebar to filter data by region, weather type, and date range
- The map shows the latest weather conditions with temperature as color and wind speed as size
- Charts update automatically based on your filter selections