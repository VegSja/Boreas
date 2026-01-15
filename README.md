```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
```

**Avalanche Data Platform**

---

## Overview

Boreas is a comprehensive data platform that collects, processes, and visualizes avalanche danger and weather data from Norwegian regions. The platform combines data from multiple sources to provide insights into avalanche conditions and weather patterns.

## Architecture

The platform consists of four main components:

| Component | Purpose | Technology |
|-----------|---------|------------|
| **dlt** | Data ingestion pipelines | DLT (Data Load Tool) |
| **dbt_boreas** | Data transformation and modeling | dbt |
| **dashboard** | Interactive visualization | Streamlit |
| **src** | Shared configuration and data models | Python |

## Data Flow

```
External APIs → DLT Pipelines → DuckDB (Bronze) → dbt Transformations → Gold Layer → Dashboard
```

1. **Extract** - DLT pipelines fetch data from external APIs
2. **Load** - Raw data is stored in DuckDB (Bronze layer)
3. **Transform** - dbt models clean and aggregate data (Silver/Gold layers)
4. **Visualize** - Streamlit dashboard displays processed data

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Boreas

# Install dependencies
uv sync

# Install dashboard dependencies (optional)
uv sync --extra dashboard
```

### Running the Data Pipeline

1. **Configure DLT settings** (see `dlt/.dlt/config.toml`)
2. **Run data ingestion**:
   ```bash
   cd dlt
   uv run python run_dlt_pipelines.py
   ```
3. **Run dbt transformations**:
   ```bash
   cd dbt_boreas
   uv run dbt run
   ```

### Launching the Dashboard

```bash
cd dashboard
uv run streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## Project Structure

```
Boreas/
├── dlt/                    # Data ingestion (DLT)
│   ├── pipelines/         # Pipeline definitions
│   ├── sources/           # Data source implementations
│   └── utils/             # Shared utilities
├── dbt_boreas/            # Data transformation (dbt)
│   ├── models/            # SQL transformation models
│   │   ├── 1_bronze/     # Raw data layer
│   │   ├── 2_silver/     # Cleaned data layer
│   │   └── 3_gold/       # Business logic layer
│   └── macros/            # dbt macros
├── dashboard/             # Streamlit visualization
├── src/                   # Shared configuration
│   ├── config/           # Region definitions
│   └── models/           # Data models
└── logs/                  # Application logs
```

## Data Sources

### Avalanche Data
- **Source**: Norwegian Avalanche Warning Service API
- **Content**: Danger levels, warnings, regional information
- **Update Frequency**: Daily

### Weather Data
- **Source**: Weather API (forecast and historical)
- **Content**: Temperature, precipitation, wind speed, humidity
- **Update Frequency**: Hourly/Daily

### Regional Data
- **Source**: Static configuration
- **Content**: 23 Norwegian avalanche regions with geographic boundaries
- **Coverage**: From Svalbard to Rogaland

## Development

### Adding New Data Sources
1. Create source implementation in `dlt/sources/`
2. Add pipeline in `dlt/pipelines/`
3. Update `dlt/run_dlt_pipelines.py`
4. Create corresponding dbt models

## Dashboard Features

- **Interactive Map**: Regional avalanche danger visualization
- **Time Series Analysis**: Historical trends and patterns
- **Weather Integration**: Correlation between weather and avalanche danger
- **Data Filters**: Region, date range, and danger level filtering

## Configuration

### DLT Configuration
- Configure API endpoints and credentials in `dlt/.dlt/config.toml`
- Adjust pipeline settings in individual pipeline files

### dbt Configuration
- Database connection settings in `dbt_boreas/profiles.yml`
- Model configurations in `dbt_boreas/dbt_project.yml`

### Dashboard Configuration
- Streamlit settings in `.streamlit/config.toml`
- Database path configuration in dashboard code

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under [LICENSE] - see the LICENSE file for details.

## Support

For questions and support:
- Create an issue in the repository
- Check the documentation in individual component folders
- Review the logs in the `logs/` directory for troubleshooting