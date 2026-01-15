```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

DASHBOARD | Interactive Avalanche Data Visualization
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
- **Access Pattern**: Read-only with intelligent caching

### Performance Optimization
| Component | Cache Duration | Purpose |
|-----------|---------------|---------|
| **Data Queries** | 5 minutes | Real-time dashboard responsiveness |
| **Coordinate Data** | 1 hour | Static geographic information |
| **Streamlit Config** | Session-based | UI theme and layout persistence |

## Configuration Management

### Streamlit Settings (`.streamlit/config.toml`)
```toml
[theme]
base = "light"
primaryColor = "#FF6B6B"

[server]
enableCORS = false
enableXsrfProtection = false
```

### Database Connection
- **Connection String**: `./boreas.duckdb` (relative path)
- **Security**: Read-only mode prevents data corruption
- **Performance**: Connection pooling with automatic cleanup

## User Interface Guide

### Navigation Workflow
1. **Sidebar Controls**: Configure filters and date ranges
2. **Interactive Map**: Regional danger level visualization
3. **Analytics Panel**: Key performance indicators and trends
4. **Data Tables**: Detailed records with export capabilities

### Advanced Features
- **Multi-date Comparison**: Parallel analysis across time periods
- **Region Clustering**: Grouped analysis by geographic proximity
- **Export Formats**: CSV, JSON data download options

## Project Structure

```
dashboard/
├── app.py                 # Main Streamlit application entry point
├── README.md             # Professional documentation (this file)
└── .streamlit/
    └── config.toml       # Dashboard configuration and theming
```

## Development Notes

### Code Architecture
- **Streamlit Components**: Modular UI components with state management
- **Data Layer**: DuckDB integration with error handling
- **Caching Strategy**: Multi-level caching for optimal performance

### Troubleshooting
| Issue | Solution |
|-------|----------|
| **No Data Displayed** | Verify DLT pipelines completed successfully |
| **Performance Issues** | Check DuckDB file permissions and disk space |
| **Map Not Loading** | Confirm coordinate data cache is populated |

---

**Documentation Standards**: Enterprise-grade technical documentation  
**Last Updated**: January 2026
