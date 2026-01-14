import dlt
from datetime import datetime, date
from typing import Iterator, Dict, Any

from src.config.regions import AVALANCHE_REGIONS
from .weather_common import fetch_weather_data
from exceptions import WeatherAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


@dlt.source
def weather_historic_source(
    start_date: str = dlt.config.value,
    hourly_params: list = dlt.config.value,
    timezone: str = dlt.config.value,
    archive_api_base_url: str = dlt.config.value,
    request_timeout: int = dlt.config.value
):
    """DLT source for historic weather data.
    
    Args:
        start_date: Start date for historic data collection
        hourly_params: List of weather parameters to fetch
        timezone: Timezone for weather data
        archive_api_base_url: Base URL for archive weather API
    
    Returns:
        List of dlt resources for historic data from all regions
    """
    if hourly_params is None:
        hourly_params = ["temperature_2m", "relative_humidity_2m", "precipitation", "windspeed_10m"]
        
    resources = []
    for region in AVALANCHE_REGIONS:
        def make_historic_resource(r=region):
            @dlt.resource(
                table_name="weather_historic",
                write_disposition="merge",
                primary_key=['time', 'region_id'],
                name=f'historic_{r.region_id}',
                schema_contract={"tables": "evolve", "columns": "freeze", "data_type": "freeze"}
            )
            def get_historic_data(
                time: dlt.sources.incremental[str] = dlt.sources.incremental(
                    "time", initial_value=start_date
                )
            ) -> Iterator[Dict[str, Any]]:
                """Fetch historic weather data for a specific region.
                
                Args:
                    time: Incremental loading state for time column
                    
                Yields:
                    Dict containing historic weather data
                """
                params = {
                    "latitude": r.center_lat,
                    "longitude": r.center_lon,
                    "start_date": datetime.strptime(time.last_value, "%Y-%m-%dT%H:%M").date().isoformat(),
                    "end_date": date.today().isoformat(),
                    "hourly": ",".join(hourly_params),
                    "timezone": timezone,
                }
                
                try:
                    yield from fetch_weather_data(
                        f"{archive_api_base_url}/archive", 
                        params, 
                        region=r,
                        request_timeout=request_timeout
                    )
                except WeatherAPIError as e:
                    logger.error(f"Failed to fetch historic data for {r.name}: {e}")
                    raise
            return get_historic_data
        resources.append(make_historic_resource())
    return resources