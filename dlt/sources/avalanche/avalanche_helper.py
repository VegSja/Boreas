from typing import Any, Dict, Iterator
from dlt.sources.helpers import requests

def fetch_avalanche_warnings_data(
    region_id: str,
    language_key: str,
    start_date: str,
    end_date:str
) -> Iterator[Dict[str, Any]]:

    url = (
        f"https://api01.nve.no/"
        f"hydrology/forecast/avalanche/v6.3.0/api/"
        f"AvalancheWarningByRegion/Simple/"
        f"{region_id}/{language_key}/{start_date}/{end_date}"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    for record in data:
        yield record