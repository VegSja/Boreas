# DLT Pipelines - Data Ingestion

Data Load Tool (DLT) pipelines for ingesting avalanche and weather data from external APIs into DuckDB.

## 🏗️ Architecture

The DLT component handles the **Extract** and **Load** phases of the ELT pipeline:
- **Extract**: Fetch data from external APIs
- **Transform**: Minimal data normalization and validation
- **Load**: Store raw data in DuckDB (Bronze layer)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- DLT >= 1.20.0
- DuckDB >= 1.4.3
- Valid API credentials (configured in `config.toml`)

### Configuration

1. **Configure DLT settings** (`.dlt/config.toml`):
```toml
[sources.avalanche_warning_source]
start_date = "2024-01-01T00:00:00"
language_key = "1"  # Norwegian
api_base_url = "https://api01.nve.no/hydrology/forecast/avalanche/v6.2.0/api"
request_timeout = 30

[sources.weather_forecast_source]
# Weather API configuration
api_base_url = "your_weather_api_url"
api_key = "your_api_key"

[sources.weather_historic_source]
# Historical weather API configuration
start_date = "2024-01-01"
```

2. **Set environment variables** (if using external credentials):
```bash
export WEATHER_API_KEY="your_api_key"
export AVALANCHE_API_TOKEN="your_token"  # if required
```

### Running Pipelines

```bash
# Navigate to DLT directory
cd dlt

# Run all pipelines
python run_dlt_pipelines.py

# Run individual pipelines
python -c "from pipelines.avalanche_pipeline import run_avalanche_pipeline; run_avalanche_pipeline()"
python -c "from pipelines.weather_pipeline import run_weather_pipeline; run_weather_pipeline()"
python -c "from pipelines.region_pipeline import run_regions_pipeline; run_regions_pipeline()"
```

## 📊 Data Sources

### 1. Avalanche Data (`sources/avalanche/`)
**Source**: Norwegian Avalanche Warning Service (NVE API)

**Files**:
- `avalanche_warnings.py` - Main data source implementation
- `avalanche_helper.py` - API interaction utilities

**Data Collected**:
- Danger levels (1-5 scale)
- Warning validity periods
- Regional information
- Warning descriptions

**Update Strategy**: Incremental with state management

### 2. Weather Data (`sources/weather/`)
**Sources**: Weather APIs (forecast + historical)

**Files**:
- `weather_forecast.py` - Current and forecast data
- `weather_historic.py` - Historical weather data
- `weather_common.py` - Shared utilities

**Data Collected**:
- Temperature (min/max)
- Precipitation
- Wind speed and direction
- Humidity
- Weather conditions

**Update Strategy**: Daily refresh for forecasts, incremental for historical

### 3. Regional Data (`sources/regions/`)
**Source**: Static configuration from `src/config/regions.py`

**Files**:
- `region_source.py` - Regional metadata loader

**Data Collected**:
- 23 Norwegian avalanche regions
- Geographic boundaries (lat/lon)
- Region identifiers and names

**Update Strategy**: Full refresh (static data)

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

### Data Schemas

**Avalanche Schema**:
```python
primary_key=['RegId', 'ValidFrom', 'ValidTo']
write_disposition="merge"  # Incremental updates
schema_contract={"tables": "evolve", "columns": "evolve"}
```

**Weather Schema**:
```python
primary_key=['region_id', 'datetime', 'forecast_type']
write_disposition="append"  # Historical accumulation
```

## 📁 File Structure

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

## 🎯 Data Quality & Validation

### Source Validation
- API response validation
- Data type checking
- Required field verification
- Geographic boundary validation

### Error Handling
```python
# Custom exceptions
from exceptions import AvalancheAPIError, WeatherAPIError

# Retry logic for API failures
@dlt.source
def avalanche_warning_source():
    try:
        data = fetch_avalanche_data()
    except AvalancheAPIError as e:
        logger.error(f"API error: {e}")
        # Implement retry or fallback logic
```

### Logging
- Structured logging with JSON format
- API request/response tracking
- Pipeline execution metrics
- Error reporting and alerting

## 🔄 Incremental Loading

### State Management
DLT automatically manages incremental state:
- **Last Run Timestamp**: Track latest data point
- **Resource State**: Per-source state management
- **Deduplication**: Automatic handling of duplicates

### Example Implementation
```python
@dlt.resource(
    write_disposition="merge",
    primary_key=['region_id', 'datetime']
)
def incremental_weather_data(
    updated_at=dlt.sources.incremental("updated_at", 
                                      initial_value="2024-01-01T00:00:00")
):
    # Fetch only new/updated records
    return fetch_weather_since(updated_at.last_value)
```

## 🔧 Monitoring & Maintenance

### Performance Monitoring
```bash
# Check pipeline state
dlt pipeline avalanche_pipeline info

# View pipeline metrics
dlt pipeline avalanche_pipeline trace

# Reset pipeline state (if needed)
dlt pipeline avalanche_pipeline drop
```

### Maintenance Tasks
- **State Reset**: When API schemas change
- **Full Refresh**: Periodic historical data updates
- **Schema Evolution**: Handle API changes gracefully

## 🐛 Troubleshooting

### Common Issues

**API Rate Limiting**:
- Implement exponential backoff
- Use request_timeout configuration
- Monitor API quotas

**Network Connectivity**:
- Check API endpoint availability
- Verify DNS resolution
- Review firewall settings

**Schema Changes**:
- Monitor API documentation for changes
- Use schema evolution features
- Test with sample data first

### Debugging
```bash
# Enable debug logging
export DLT_DEBUG=1

# Run with verbose output
python run_dlt_pipelines.py --verbose

# Check pipeline logs
tail -f logs/dlt.log
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