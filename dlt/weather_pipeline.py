import dlt
from dlt.sources.helpers import requests
import datetime


OSLO_LAT = 59.9139
OSLO_LON = 10.7522

@dlt.resource(
    table_name="weather_historic", 
    write_disposition="merge",
    primary_key="time"
)
def get_weather_data_historic(
    time: dlt.sources.incremental[str] = dlt.sources.incremental(
        "time", initial_value="2026-01-01T00:00"
    )
):
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    end_date = datetime.date.today().isoformat()

    params = {
        "latitude": OSLO_LAT,
        "longitude": OSLO_LON,
        "start_date": datetime.datetime.strptime(time.last_value, "%Y-%m-%dT%H:%M").date().isoformat(),
        "end_date": end_date,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "windspeed_10m"
        ]),
        "timezone": "Europe/Oslo",
    }
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    data = r.json()
    hourly = data["hourly"]

    keys = list(hourly.keys())
    n = len(hourly[keys[0]])
    records = [{k: hourly[k][i] for k in keys} for i in range(n)]
    
    loaded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    for rec in records:
        rec["loaded_at"] = loaded_at
        rec["type"] = "archive"
    
    yield records



@dlt.resource(
    table_name="weather_forecast", 
    write_disposition="merge",
    primary_key="time"
)
def get_weather_data_forecast():
    
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": OSLO_LAT,
        "longitude": OSLO_LON,
        "hourly": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "windspeed_10m"
        ]),
        "timezone": "Europe/Oslo",
    }
    
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()

    data = r.json()
    hourly = data["hourly"]

    keys = list(hourly.keys())
    n = len(hourly[keys[0]])
    records = [{k: hourly[k][i] for k in keys} for i in range(n)]
    
    loaded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    for rec in records:
        rec["loaded_at"] = loaded_at
    
    yield records



@dlt.source
def get_source():
    return [get_weather_data_historic, get_weather_data_forecast]

pipeline = dlt.pipeline(
    pipeline_name="weather_pipeline",
    destination=dlt.destinations.duckdb(
        destination_name='../boreas',
        enable_dataset_name_normalization=False
    ),
    dataset_name="1_bronze"
)

load_info = pipeline.run(get_source())
row_counts  = pipeline.last_trace.last_normalize_info

print(row_counts)
print("--------")
print(load_info)
