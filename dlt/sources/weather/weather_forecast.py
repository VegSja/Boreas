import dlt
from typing import Iterator, Dict, Any

from src.config.regions import AVALANCHE_REGIONS
from .weather_common import fetch_weather_data, HOURLY_PARAMS, TIMEZONE


@dlt.source
def weather_forecast_source():
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
                
                params = {
                    "latitude": r.center_lat,
                    "longitude": r.center_lon,
                    "hourly": ",".join(HOURLY_PARAMS),
                    "timezone": TIMEZONE,
                }
                
                try:
                    yield from fetch_weather_data("https://api.open-meteo.com/v1/forecast", params, region=r)
                except Exception as e:
                    print(f"Failed to fetch forecast data for {r.name}: {e}")
            return get_forecast_data
        resources.append(make_forecast_resource())
    return resources