import requests
from typing import List, Dict, Any

from requests import RequestException

from app.services.scraper.Constants.avalanche_regions import AvalancheRegion
from app.services.scraper.data_classes.avalache_data import VarsomAvalancheResponse


def get_avalanche_data(region: AvalancheRegion, start_date: str, end_date: str) -> List[VarsomAvalancheResponse]:
    url = generate_url(region.region_id, start_date, end_date)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == requests.codes.ok:
        try:
            parsed: List[Dict[str, Any]] = response.json()
            warnings: List[VarsomAvalancheResponse] = [
                VarsomAvalancheResponse(**data) for data in parsed
            ]
            return warnings
        except Exception as err:
            raise(ValueError(f"The response we recieved from Varsom's API did not match what we expected: {err}"))
    else:
        raise(RequestException("Uh oh! Something unexpected happened during avalanche fetching"))


def generate_url(region_id: str, start_date: str, end_date: str) -> str:
    language_key = "1" # Norwegian
    url = f"https://api01.nve.no/hydrology/forecast/avalanche/v6.2.1/api/AvalancheWarningByRegion/Simple/{region_id}/{language_key}/{start_date}/{end_date}"
    return url
