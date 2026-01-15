# DLT Pipelines - Data Ingestion

Data Load Tool (DLT) pipelines for ingesting avalanche and weather data from external APIs into DuckDB.

## Architecture

The DLT component handles the **Extract** and **Load** phases of the ELT pipeline:
- **Extract**: Fetch data from external APIs
- **Transform**: Minimal data normalization and validation
- **Load**: Store raw data in DuckDB (Bronze layer)

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- DLT >= 1.20.0
- DuckDB >= 1.4.3
- Valid API credentials (configured in `config.toml`)


### Running Pipelines

```bash
# Run all pipelines
uv run dlt/run_dlt_pipelines.py
```

## 🔧 Pipeline Configuration

### Pipeline Definitions (`pipelines/`)

**avalanche_pipeline.py**:
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

**Features**:
- **Destination**: DuckDB database
- **Schema**: `1_bronze` (bronze layer)
- **Progress**: Visual progress bars
- **State Management**: Automatic incremental loading

## File Structure

```
dlt/
├── pipelines/
│   ├── avalanche_pipeline.py    # Avalanche data pipeline
│   ├── weather_pipeline.py      # Weather data pipeline
│   └── region_pipeline.py       # Region metadata pipeline
├── sources/
│   ├── avalanche/
│   │   ├── avalanche_warnings.py
│   │   └── avalanche_helper.py
│   ├── weather/
│   │   ├── weather_forecast.py
│   │   ├── weather_historic.py
│   │   └── weather_common.py
│   └── regions/
│       └── region_source.py
├── utils/
│   └── logging.py               # Logging configuration
├── .dlt/
│   └── config.toml             # DLT configuration
├── exceptions.py               # Custom exceptions
└── run_dlt_pipelines.py        # Main execution script
```

## Data Quality & Validation

### Logging
- Structured logging with JSON format
- API request/response tracking
- Pipeline execution metrics
- Error reporting and alerting

## 🔧 Monitoring & Maintenance

### Performance Monitoring
```bash
# Check pipeline state
uv run dlt pipeline avalanche_pipeline info

# View pipeline metrics
uv run dlt pipeline avalanche_pipeline trace

# Reset pipeline state (if needed)
uv run dlt pipeline avalanche_pipeline drop
```

## 🔗 Integration

### Upstream Dependencies
- External API availability
- Network connectivity
- Valid authentication credentials

### Downstream Integration
- Outputs to DuckDB (`../boreas.duckdb`)
- Consumed by dbt transformations
- Bronze layer tables for analytics

## 📚 Resources

- [DLT Documentation](https://dlthub.com/docs)
- [DuckDB Integration](https://dlthub.com/docs/dlt-ecosystem/destinations/duckdb)
- [Source Development Guide](https://dlthub.com/docs/walkthroughs/create-a-pipeline)