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

Professional Streamlit dashboard for real-time visualization of avalanche danger levels and weather conditions across Norwegian regions. Features interactive maps, time-series analysis, comprehensive data analytics, and a dedicated **Data Profiling** page for data quality monitoring.

## Core Features

| Feature Category | Description | Key Capabilities |
|------------------|-------------|------------------|
| **Interactive Mapping** | Real-time regional visualization | Color-coded danger levels, hover details, date selection |
| **Time Series Analytics** | Historical trend analysis | Date range filtering, danger level heatmaps |
| **Weather Integration** | Comprehensive meteorological data | Temperature ranges, precipitation, wind conditions |
| **Data Profiling** | Data quality monitoring | Missing value analysis, outlier detection, distributions, correlations |
| **Data Export** | Professional reporting tools | Tabular views, metrics dashboard, filtering |

## Quick Start

### System Requirements
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Completed data pipeline (DLT + dbt transformations)
- DuckDB database with processed avalanche/weather data

### Option 1 – Local (uv)

```bash
# Install dashboard dependencies
uv sync --extra dashboard

# Verify data availability
cd dlt && uv run python run_dlt_pipelines.py
cd ../dbt_boreas && uv run dbt run

# Launch dashboard (run from repo root so boreas.duckdb is resolved correctly)
uv run streamlit run dashboard/app.py
```

**Access Point**: `http://localhost:8501`

### Option 2 – Docker (recommended)

The dashboard ships with a `Dockerfile` and `docker-compose.yml` at the repo root.
Run the full pipeline first to produce `boreas.duckdb`, then:

```bash
# Build and start the container
docker compose up --build

# Or run in the background
docker compose up --build -d
```

**Access Point**: `http://localhost:8501`

The container mounts `./boreas.duckdb` in read-only mode.
Stop with `docker compose down`.

#### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOREAS_DB_PATH` | `/app/boreas.duckdb` | Path to the DuckDB database inside the container |

## Dashboard Pages

### 🌨️ Main Dashboard (`app.py`)

- **Map view** – avalanche danger and weather variable maps side-by-side
- **Heatmap** – danger level by region over time
- **Summary tables** – recent avalanche and weather records

### 🔍 Data Profiling (`pages/1_Data_Profiling.py`)

Navigate to **Data Profiling** in the sidebar to access:

| Section | Description |
|---------|-------------|
| **🚨 Alerts** | Automatic banner flagging missing value issues (>20 %) and outlier columns (>5 % outliers) |
| **📋 Overview** | Record counts, date ranges, and missing value bar charts for both datasets |
| **📊 Distributions** | Histograms and box plots for danger levels and every weather variable |
| **⚠️ Outliers & Anomalies** | IQR-based outlier summary table, time-series view highlighting anomalous data points, and danger level range validation |
| **🔗 Correlations** | Pearson correlation heatmap and descriptive statistics for weather variables |

#### Outlier Detection Method

Outliers are identified using the **IQR (Interquartile Range)** method:

```
lower_bound = Q1 − 1.5 × IQR
upper_bound = Q3 + 1.5 × IQR
```

Values outside `[lower_bound, upper_bound]` are flagged as outliers and highlighted in red on charts and in the alert banner.

## Technical Architecture

### Data Pipeline Integration
- **Source**: Gold layer models from dbt transformations
- **Tables**: `3_gold.avalanche_per_region`, `3_gold.weather_per_region`
- **Database**: DuckDB (`boreas.duckdb`, path configurable via `BOREAS_DB_PATH`)

## Project Structure

```
dashboard/
├── app.py                 # Main Streamlit application (maps, heatmaps, tables)
├── pages/
│   └── 1_Data_Profiling.py  # Data profiling & quality monitoring page
├── README.md              # This file
└── .streamlit/
    └── config.toml        # Dashboard configuration and theming
```

