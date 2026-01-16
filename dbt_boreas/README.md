```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

DBT TRANSFORMATIONS 
```

# dbt Boreas - Data Transformation Engine

Production-grade dbt project implementing medallion architecture for avalanche and weather data processing. Transforms raw ingestion data into analytics-ready datasets with comprehensive data quality controls and lineage tracking.

## Medallion Architecture

| Layer | Schema | Purpose | 
|-------|--------|---------|
| **Bronze** | `1_bronze` | Raw data ingestion from DLT pipelines |
| **Silver** | `2_silver` | Cleaned, standardized, deduplicated, modelled data |
| **Gold** | `3_gold` | Business logic, aggregations, analytics |

### Data Flow Pipeline
```
DLT Sources → Bronze Layer → Silver Layer → Gold Layer → Dashboard/Analytics
```

## Quick Start Guide

### System Requirements
| Component | Version | Purpose |
|-----------|---------|---------|
| **dbt-core** | >= 1.11.2 | Transformation engine |
| **dbt-duckdb** | >= 1.10.0 | DuckDB adapter |
| **DuckDB** | >= 1.4.3 | Analytics database |
| **uv** | Latest | Package management |

### Setup & Configuration

```bash
# Install project dependencies
uv sync

# Navigate to dbt directory
cd dbt_boreas

# Install dbt packages
uv run dbt deps

# Execute full transformation pipeline
uv run dbt build

# Validate data quality
uv run dbt test
```

## Advanced Operations

### Selective Execution
```bash
# Layer-specific execution
uv run dbt run --select models/2_silver+    # Silver and downstream
uv run dbt run --select models/3_gold       # Gold layer only

# Model-specific operations
uv run dbt run --select fact_weather+       # Model and dependencies
uv run dbt test --select dim_regions        # Test specific model

# Full refresh for schema changes
uv run dbt run --full-refresh --select models/2_silver
```

### Development Workflow
```bash
# Incremental development
uv run dbt run --select state:modified+     # Changed models only
uv run dbt build --select +my_model+        # Full dependency chain

# Documentation generation
uv run dbt docs generate && uv run dbt docs serve
```

## Project Structure

```
dbt_boreas/
├── models/
│   ├── 1_bronze/
│   │   └── sources.yml                    # Source table definitions
│   ├── 2_silver/
│   │   ├── dim_regions.sql               # Regional dimension
│   │   ├── fact_avalanche_danger.sql     # Avalanche fact table
│   │   ├── fact_weather.sql              # Weather fact table
│   │   └── schema.yml                    # Model documentation & tests
│   └── 3_gold/
│       ├── avalanche_average_weather_per_region.sql
│       └── schema.yml                    # Analytics documentation
├── macros/
│   └── generate_schema_name.sql          # Custom schema logic
├── dbt_project.yml                       # Project configuration
├── profiles.yml                          # Database connections
├── packages.yml                          # Package dependencies
└── README.md                             # This documentation
```

## Integration & Dependencies

### Upstream Systems
- **DLT Pipelines**: Data ingestion prerequisite
- **Source APIs**: Norwegian avalanche/weather services
- **DuckDB Database**: Raw data storage

### Downstream Consumers
- **Streamlit Dashboard**: Real-time visualization
- **Analytics Tools**: Business intelligence platforms
- **Data Exports**: CSV/JSON output formats

## Production Operations

### Environment Management
```bash
# Development execution
uv run dbt run --target dev

# Production deployment
uv run dbt run --target prod --full-refresh

# Complete pipeline with testing
uv run dbt build --target prod
```
