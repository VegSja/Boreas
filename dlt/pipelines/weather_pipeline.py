import dlt
import os
from sources.weather.weather_historic import weather_historic_source
from sources.weather.weather_forecast import weather_forecast_source


def create_weather_pipeline():
    """Create and configure the weather data pipeline."""
    # Get absolute path to project root (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'boreas.duckdb')
    
    pipeline = dlt.pipeline(
        pipeline_name="weather_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name=db_path,
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='enlighten'
    )
    return pipeline


def run_weather_pipeline():
    """Run the complete weather data pipeline."""
    pipeline = create_weather_pipeline()
    pipeline.run([weather_historic_source(), weather_forecast_source()])