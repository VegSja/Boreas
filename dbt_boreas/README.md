```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

DBT TRANSFORMATIONS | Enterprise Data Engineering
```

# dbt Boreas - Data Transformation Engine

Production-grade dbt project implementing medallion architecture for avalanche and weather data processing. Transforms raw ingestion data into analytics-ready datasets with comprehensive data quality controls and lineage tracking.

## Medallion Architecture

| Layer | Schema | Purpose | Materialization |
|-------|--------|---------|----------------|
| **Bronze** | `1_bronze` | Raw data ingestion from DLT pipelines | `table` |
| **Silver** | `2_silver` | Cleaned, standardized, deduplicated data | `table` |
| **Gold** | `3_gold` | Business logic, aggregations, analytics | `table` |

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
uv run dbt run

# Validate data quality
uv run dbt test
```

**Database Configuration** (`profiles.yml`):
```yaml
dbt_boreas:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: '../boreas.duckdb'
      schema: main
```

## Data Model Architecture

### Bronze Layer (`1_bronze`) - Source Integration
| Source Table | Description | Update Frequency |
|--------------|-------------|------------------|
| `avalanche_danger_levels` | Raw avalanche warnings from Norwegian authorities | Daily |
| `weather_forecast` | Meteorological forecast data | 6-hourly |
| `weather_historic` | Historical weather observations | Daily |
| `regions` | Geographic boundaries and metadata | Static |

### Silver Layer (`2_silver`) - Data Standardization
| Model | Purpose | Key Transformations |
|-------|---------|-------------------|
| `fact_avalanche_danger` | Standardized avalanche records | Type casting, null handling, deduplication |
| `fact_weather` | Unified weather dataset | Forecast/historic union, field normalization |
| `dim_regions` | Regional dimension table | Geographic boundary standardization |

### Gold Layer (`3_gold`) - Business Analytics
| Model | Description | Business Value |
|-------|-------------|---------------|
| `avalanche_average_weather_per_region` | Regional weather aggregated with danger levels | Dashboard analytics, trend analysis |

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

## Technical Configuration

### Project Configuration (`dbt_project.yml`)
```yaml
models:
  dbt_boreas:
    1_bronze:
      +materialized: table
      +schema: 1_bronze
    2_silver:
      +materialized: table
      +schema: 2_silver
    3_gold:
      +materialized: table
      +schema: 3_gold
```

### Data Quality Framework
| Validation Type | Implementation | Frequency |
|----------------|---------------|-----------|
| **Primary Key Constraints** | Unique tests on ID fields | Every run |
| **Not-Null Validations** | Required field checks | Every run |
| **Referential Integrity** | Foreign key relationships | Every run |
| **Data Freshness** | Source table recency | Daily |

### Performance Optimization
- **Full Table Materialization**: Optimized for analytics workloads
- **Schema Separation**: Logical layer isolation for clarity
- **Incremental Capability**: Available for high-volume datasets
- **Custom Macros**: Schema naming and utility functions

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

### Monitoring & Maintenance
| Metric | Monitoring | Alerting |
|--------|------------|----------|
| **Model Success Rate** | dbt logs | Email notifications |
| **Data Freshness** | Source table checks | Slack alerts |
| **Test Failures** | Quality validations | Dashboard warnings |

---

**Enterprise Documentation Standards**  
**Architecture**: Medallion (Bronze → Silver → Gold)  
**Last Updated**: January 2026