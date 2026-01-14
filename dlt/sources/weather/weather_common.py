from dlt.sources.helpers import requests
from datetime import datetime, timezone
from typing import Iterator, Dict, Any

from src.models.regions import AvalancheRegion

HOURLY_PARAMS = [
    "temperature_2m",
    "relative_humidity_2m", 
    "precipitation",
    "windspeed_10m"
]
TIMEZONE = "Europe/Oslo"


def fetch_weather_data(url: str, params: Dict[str, Any], region: AvalancheRegion) -> Iterator[Dict[str, Any]]:
    """Fetch and process weather data from Open Meteo API."""

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