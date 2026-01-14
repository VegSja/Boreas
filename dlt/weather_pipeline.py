from alive_progress import alive_bar
import dlt
from dlt.sources.helpers import requests
from datetime import datetime, date, timezone
from typing import Iterator, Dict, Any

from src.config.regions import AVALANCHE_REGIONS
from src.models.regions import AvalancheRegion

START_DATE = "2026-01-10:T00:00"
HOURLY_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m", 
    "precipitation",
    "windspeed_10m"
]
TIMEZONE = "Europe/Oslo"


def fetch_weather_data(url: str, params: Dict[str, Any], region: AvalancheRegion) -> Iterator[Dict[str, Any]]:
    """Fetch and process weather data from Open Meteo API."""
    print(f"Fetching data for {region.name}...")

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    hourly = data["hourly"]
    
    loaded_at = datetime.now(timezone.utc).isoformat()
    
    for i in range(len(hourly["time"])):
        record = {key: hourly[key][i] for key in hourly.keys()}
        record["loaded_at"] = loaded_at
        record['region_id'] = region.region_id
        record['region_name'] = region.name
        yield record

@dlt.source
def weather_historic_source():
    resources = []
    for region in AVALANCHE_REGIONS:
        def make_historic_resource(r=region):
            @dlt.resource(
                table_name="weather_historic",
                write_disposition="merge",
                primary_key=['time', 'region_id'],
                name=f'historic_{r.region_id}'
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
                    print(f"Failed to fetch data fro {r.name}: {e}")
            return get_historic_data
        resources.append(make_historic_resource())
    return resources

@dlt.source
def weather_forecast_source():
    resources = []
    for region in AVALANCHE_REGIONS:
        def make_forecast_resource(r=region):
            @dlt.resource(
                table_name="weather_forecast",
                write_disposition="merge",
                primary_key=['time', 'region_id'],
                name=f'forecast_{r.region_id}'
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
                    print(f"Failed to fetch data fro {r.name}: {e}")
            return get_forecast_data
        resources.append(make_forecast_resource())
    return resources



if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="weather_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name='../boreas',
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='enlighten'
    )
    
    load_info = pipeline.run([weather_historic_source(), weather_forecast_source()])
    row_counts = pipeline.last_trace.last_normalize_info
    
    print(row_counts)
    print("--------")  
    print(load_info)
