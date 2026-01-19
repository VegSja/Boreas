# dagster_boreas/assets/dlt_assets.py
import os
import sys

# Add dlt_boreas to path BEFORE importing dlt package
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "dlt_boreas"))

import dlt  # Now imports the actual dlt package, not our folder
from dagster import asset, AssetExecutionContext, MaterializeResult, MetadataValue

DB_PATH = os.path.join(PROJECT_ROOT, "boreas")

# Import your existing DLT sources
from sources.regions.region_source import regions_source
from sources.avalanche.avalanche_warnings import avalanche_warning_source
from sources.weather.weather_forecast import weather_forecast_source
from sources.weather.weather_historic import weather_historic_source
from sources.grids.weather_grids_source import weather_grids_source


def create_dlt_pipeline(pipeline_name: str) -> dlt.Pipeline:
    """Factory function to create a DLT pipeline with standard config."""
    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=dlt.destinations.duckdb(
            destination_name=DB_PATH,
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress="log"  # Use log progress for Dagster compatibility
    )


@asset(
    group_name="bronze",
    compute_kind="dlt",
    description="Load regions data from API to bronze layer"
)
def regions_bronze(context: AssetExecutionContext) -> MaterializeResult:
    """Extract and load regions data using DLT."""
    pipeline = create_dlt_pipeline("region_pipeline")
    pipeline.sync_destination()
    
    load_info = pipeline.run(regions_source())
    
    context.log.info(f"Loaded regions data: {load_info}")
    
    return MaterializeResult(
        metadata={
            "rows_loaded": MetadataValue.int(load_info.metrics.get("rows", 0)),
            "destination": MetadataValue.text(str(pipeline.destination)),
        }
    )


@asset(
    group_name="bronze",
    compute_kind="dlt",
    description="Load weather grids reference data to bronze layer"
)
def weather_grids_bronze(context: AssetExecutionContext) -> MaterializeResult:
    """Extract and load weather grids data using DLT."""
    pipeline = create_dlt_pipeline("weather_grids_pipeline")
    pipeline.sync_destination()
    
    load_info = pipeline.run(weather_grids_source())
    
    context.log.info(f"Loaded weather grids data: {load_info}")
    
    return MaterializeResult(
        metadata={
            "destination": MetadataValue.text(str(pipeline.destination)),
        }
    )


@asset(
    group_name="bronze",
    compute_kind="dlt",
    deps=[weather_grids_bronze],  # Depends on grids being loaded first
    description="Load historic weather data to bronze layer"
)
def weather_historic_bronze(context: AssetExecutionContext) -> MaterializeResult:
    """Extract and load historic weather data using DLT."""
    pipeline = create_dlt_pipeline("weather_historic_pipeline")
    pipeline.sync_destination()
    
    load_info = pipeline.run(weather_historic_source())
    
    context.log.info(f"Loaded historic weather data: {load_info}")
    
    return MaterializeResult(
        metadata={
            "destination": MetadataValue.text(str(pipeline.destination)),
        }
    )


@asset(
    group_name="bronze",
    compute_kind="dlt",
    deps=[weather_grids_bronze],
    description="Load weather forecast data to bronze layer"
)
def weather_forecast_bronze(context: AssetExecutionContext) -> MaterializeResult:
    """Extract and load weather forecast data using DLT."""
    pipeline = create_dlt_pipeline("weather_forecast_pipeline")
    pipeline.sync_destination()
    
    load_info = pipeline.run(weather_forecast_source())
    
    context.log.info(f"Loaded weather forecast data: {load_info}")
    
    return MaterializeResult(
        metadata={
            "destination": MetadataValue.text(str(pipeline.destination)),
        }
    )


@asset(
    group_name="bronze",
    compute_kind="dlt",
    deps=[regions_bronze],  # Avalanche warnings need regions
    description="Load avalanche warnings data to bronze layer"
)
def avalanche_bronze(context: AssetExecutionContext) -> MaterializeResult:
    """Extract and load avalanche warnings using DLT."""
    pipeline = create_dlt_pipeline("avalanche_pipeline")
    pipeline.sync_destination()
    
    load_info = pipeline.run(avalanche_warning_source())
    
    context.log.info(f"Loaded avalanche data: {load_info}")
    
    return MaterializeResult(
        metadata={
            "destination": MetadataValue.text(str(pipeline.destination)),
        }
    )