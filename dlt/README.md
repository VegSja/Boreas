```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

DLT PIPELINES | Production Data Ingestion Engine
```

# DLT Pipelines - Enterprise Data Ingestion

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

# Monitor pipeline progress
tail -f ../logs/dlt_pipeline.log
```

### Configuration Requirements
- Valid API credentials in `.dlt/config.toml`
- Network connectivity to Norwegian data services
- Write permissions to database directory

## Pipeline Architecture

### Core Pipeline Configuration
```python
def create_avalanche_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="avalanche_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name=db_path,
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='enlighten'
    )
    return pipeline
```

### Pipeline Specifications
| Pipeline | Source API | Update Frequency | Data Volume |
|----------|------------|------------------|-------------|
| **avalanche_pipeline** | Norwegian Avalanche Service | Daily | ~200 warnings/day |
| **weather_pipeline** | MET Norway API | 6-hourly | ~1000 observations/day |
| **region_pipeline** | Geographic boundaries | Weekly | Static reference data |

### Advanced Features
- **Incremental Loading**: Automatic state management
- **Schema Evolution**: Dynamic table updates
- **Parallel Processing**: Concurrent API requests
- **Progress Monitoring**: Real-time execution tracking
- **Error Recovery**: Automatic retry mechanisms

## Data Sources Integration

### External API Endpoints
| Service | Endpoint | Authentication | Rate Limits |
|---------|----------|---------------|-------------|
| **Avalanche Warnings** | `api.nve.no/avalanche` | API Key | 100 req/min |
| **Weather Data** | `api.met.no/weatherapi` | User-Agent | 1000 req/hour |
| **Geographic Regions** | `data.norge.no/` | Open | No limits |

### Data Validation Framework
```python
# Schema validation
@dlt.resource(
    table_name="avalanche_danger_levels",
    write_disposition="merge",
    primary_key="warning_id"
)
def avalanche_warnings():
    # API integration with validation
    return validated_data
```

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

### Logging & Error Handling
| Component | Log Level | Destination | Purpose |
|-----------|-----------|-------------|---------|
| **API Requests** | INFO | JSON logs | Request/response tracking |
| **Data Validation** | WARN | Console + file | Quality alerts |
| **Pipeline Errors** | ERROR | Email + Slack | Immediate notification |
| **Performance** | DEBUG | Metrics store | Optimization analysis |

### Quality Assurance
- **Schema Validation**: Automatic data type checking
- **Primary Key Constraints**: Duplicate prevention
- **Freshness Monitoring**: Data recency validation
- **API Health Checks**: Endpoint availability monitoring

## Integration Points

### Upstream Dependencies
- **API Availability**: External service uptime
- **Authentication**: Valid credentials and tokens
- **Network Access**: Firewall and proxy configuration

### Downstream Systems
- **DuckDB Database**: Raw data storage (`../boreas.duckdb`)
- **dbt Transformations**: Bronze layer consumption
- **Analytics Pipeline**: Dashboard data preparation

---

**Production Standards**: Enterprise-grade data ingestion  
**Framework**: DLT (Data Load Tool)  
**Last Updated**: January 2026