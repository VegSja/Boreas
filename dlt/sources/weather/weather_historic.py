import dlt
from datetime import datetime, date
from typing import Iterator, Dict, Any

from src.config.regions import AVALANCHE_REGIONS
from .weather_common import fetch_weather_data, HOURLY_PARAMS, TIMEZONE

START_DATE = "2026-01-10T00:00"


@dlt.source
def weather_historic_source():
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
                    "time", initial_value=START_DATE
                )
            ) -> Iterator[Dict[str, Any]]:
                
                params = {
                    "latitude": r.center_lat,
                    "longitude": r.center_lon,
                    "start_date": datetime.strptime(time.last_value, "%Y-%m-%dT%H:%M").date().isoformat(),
                    "end_date": date.today().isoformat(),
                    "hourly": ",".join(HOURLY_PARAMS),
                    "timezone": TIMEZONE,
                }
                
                try: 
                    yield from fetch_weather_data("https://archive-api.open-meteo.com/v1/archive", params, region=r)
                except Exception as e:
                    print(f"Failed to fetch historic data for {r.name}: {e}")
            return get_historic_data
        resources.append(make_historic_resource())
    return resources