```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

DLT PIPELINES 
```

# DLT Pipelines

Production-grade Data Load Tool (DLT) pipelines for real-time ingestion of Norwegian avalanche warnings, weather forecasts, and geographic data. Features automated incremental loading, comprehensive error handling, and enterprise monitoring capabilities.

## ELT Pipeline Architecture

| Phase | Component | Responsibility | Technology |
|-------|-----------|----------------|------------|
| **Extract** | API Sources | Fetch external data | HTTP clients, authentication |
| **Load** | DLT Pipelines | Raw data ingestion | DLT framework, DuckDB |
| **Transform** | dbt Models | Analytics preparation | dbt transformations |

### Data Flow
```
Norwegian APIs → DLT Sources → DuckDB Bronze → dbt Silver/Gold → Dashboard
```

## Quick Start Guide

### System Requirements
| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12+ | Runtime environment |
| **DLT** | >= 1.20.0 | Data pipeline framework |
| **DuckDB** | >= 1.4.3 | Analytics database |
| **uv** | Latest | Dependency management |

### Pipeline Execution
```bash
# Execute all data pipelines
cd dlt
uv run python run_dlt_pipelines.py
```

### Configuration Requirements
- Valid API credentials in `.dlt/config.toml`
- Network connectivity to Norwegian data services
- Write permissions to database directory

## Pipeline Architecture

### Pipeline Specifications
| Pipeline | Source API |
|----------|------------|
| **avalanche_pipeline** | Norwegian Avalanche Service |
| **weather_pipeline** | MET Norway API |
| **region_pipeline** | Geographic boundaries |

## Data Sources Integration

### External API Endpoints
| Service | Endpoint | Authentication |
|---------|----------|---------------|
| **Avalanche Warnings** | `api.nve.no/avalanche` | Open | NA |
| **Weather Data** | `api.met.no/weatherapi` | Open | NA |


## Project Structure

```
dlt/
├── pipelines/                          # Pipeline definitions
│   ├── avalanche_pipeline.py          # Avalanche danger data
│   ├── weather_pipeline.py            # Weather & meteorology
│   └── region_pipeline.py             # Geographic boundaries
├── sources/                            # Data source implementations
│   ├── avalanche/
│   │   ├── avalanche_warnings.py      # API client & validation
│   │   └── avalanche_helper.py        # Utility functions
│   ├── weather/
│   │   ├── weather_forecast.py        # Forecast data source
│   │   ├── weather_historic.py        # Historical observations
│   │   └── weather_common.py          # Shared utilities
│   └── regions/
│       └── region_source.py           # Geographic data source
├── utils/
│   └── logging.py                     # Structured logging
├── .dlt/
│   └── config.toml                    # Configuration & secrets
├── exceptions.py                      # Custom error handling
└── run_dlt_pipelines.py              # Main orchestrator
```

## Production Operations

### Monitoring & Observability
```bash
# Pipeline health checks
uv run dlt pipeline avalanche_pipeline info

# Execution metrics & performance
uv run dlt pipeline avalanche_pipeline trace

# State management operations
uv run dlt pipeline avalanche_pipeline drop  # Reset state
```

## Integration Points

### Upstream Dependencies
- **API Availability**: External service uptime

### Downstream Systems
- **DuckDB Database**: Raw data storage (`../boreas.duckdb`)
- **dbt Transformations**: Bronze layer consumption
- **Analytics Pipeline**: Dashboard data preparation

---
