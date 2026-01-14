import dlt
from typing import Iterator, Dict, Any

from src.config.regions import AVALANCHE_REGIONS
from .weather_common import fetch_weather_data
from exceptions import WeatherAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


@dlt.source
def weather_forecast_source(
    hourly_params: list = dlt.config.value,
    timezone: str = dlt.config.value,
    api_base_url: str = dlt.config.value,
    request_timeout: int = dlt.config.value
):
    """DLT source for weather forecast data.
    
    Args:
        hourly_params: List of weather parameters to fetch
        timezone: Timezone for weather data
        api_base_url: Base URL for weather API
    
    Returns:
        List of dlt resources for forecast data from all regions
    """
    if hourly_params is None:
        hourly_params = ["temperature_2m", "relative_humidity_2m", "precipitation", "windspeed_10m"]
        
    resources = []
    for region in AVALANCHE_REGIONS:
        def make_forecast_resource(r=region):
            @dlt.resource(
                table_name="weather_forecast",
                write_disposition="replace",
                primary_key=['time', 'region_id'],
                name=f'forecast_{r.region_id}',
                schema_contract={"tables": "evolve", "columns": "freeze", "data_type": "freeze"}
            )
            def get_forecast_data() -> Iterator[Dict[str, Any]]:
                """Fetch forecast data for a specific region.
                
                Yields:
                    Dict containing forecast weather data
                """
                params = {
                    "latitude": r.center_lat,
                    "longitude": r.center_lon,
                    "hourly": ",".join(hourly_params),
                    "timezone": timezone,
                }
                
                try:
                    yield from fetch_weather_data(
                        f"{api_base_url}/forecast", 
                        params, 
                        region=r,
                        request_timeout=request_timeout
                    )
                except WeatherAPIError as e:
                    logger.error(f"Failed to fetch forecast data for {r.name}: {e}")
                    raise
            return get_forecast_data
        resources.append(make_forecast_resource())
    return resources