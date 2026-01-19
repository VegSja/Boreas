import dlt
from datetime import datetime, date, timedelta
from typing import Iterator, Dict, Any
import time as time_module

from src.config.weather_grids import WEATHER_GRID_SQUARES
from .weather_common import fetch_weather_data
from exceptions import WeatherAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


def date_range_chunks(start: date, end: date, chunk_days: int) -> Iterator[tuple[date, date]]:
    """Split a date range into smaller chunks."""
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


@dlt.source
def weather_historic_source(
    start_date: str = dlt.config.value,
    hourly_params: list = dlt.config.value,
    timezone: str = dlt.config.value,
    archive_api_base_url: str = dlt.config.value,
    request_timeout: int = dlt.config.value,
    chunk_days: int = 30,
):
    """DLT source for historic weather data."""
    if hourly_params is None:
        hourly_params = ["temperature_2m", "relative_humidity_2m", "snowfall", "rain", "snow_depth", "windspeed_10m"]
        
    resources = []
    for grid in WEATHER_GRID_SQUARES:
        def make_historic_resource(g=grid):
            @dlt.resource(
                table_name="weather_historic",
                write_disposition="merge",
                primary_key=['time', 'grid_id'],
                name=f'historic_{g.grid_id}',
                schema_contract={"tables": "evolve", "columns": "freeze", "data_type": "freeze"}
            )
            def get_historic_data(
                time: dlt.sources.incremental[str] = dlt.sources.incremental(
                    "time", initial_value=start_date
                )
            ) -> Iterator[Dict[str, Any]]:
                start = datetime.strptime(time.last_value, "%Y-%m-%dT%H:%M").date()
                end = date.today()
                
                for chunk_start, chunk_end in date_range_chunks(start, end, chunk_days):
                    logger.info(f"Fetching {g.grid_id}: {chunk_start} to {chunk_end}")
                    
                    params = {
                        "latitude": g.center_lat,
                        "longitude": g.center_lon,
                        "start_date": chunk_start.isoformat(),
                        "end_date": chunk_end.isoformat(),
                        "hourly": ",".join(hourly_params),
                        "timezone": timezone,
                    }
                    
                    try:
                        for record in fetch_weather_data(
                            f"{archive_api_base_url}/archive", 
                            params, 
                            region=g,
                            request_timeout=request_timeout
                        ):
                            yield record
                        
                    except WeatherAPIError as e:
                        logger.error(f"Failed at {g.grid_id} ({chunk_start} to {chunk_end}): {e}")
                        raise
                        
            return get_historic_data
        resources.append(make_historic_resource())
    return resources