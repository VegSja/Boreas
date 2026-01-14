import dlt
from sources.weather.weather_historic import weather_historic_source
from sources.weather.weather_forecast import weather_forecast_source


def create_weather_pipeline():
    """Create and configure the weather data pipeline."""
    pipeline = dlt.pipeline(
        pipeline_name="weather_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name='../boreas',
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='alive_progress'
    )
    return pipeline


def run_weather_pipeline():
    """Run the complete weather data pipeline."""
    pipeline = create_weather_pipeline()
    pipeline.run([weather_historic_source(), weather_forecast_source()])