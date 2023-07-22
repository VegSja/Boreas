from typing import List, Dict, Any
import requests

from requests import RequestException

from Constants.avalanche_regions import AvalancheRegion
from data_classes.avalache_data import VarsomAvalancheResponse


def get_avalanche_data(
    region: AvalancheRegion, start_date: str, end_date: str
) -> List[VarsomAvalancheResponse]:
    """
    Retrieve avalanche data from Varsom's
     API for a specific region and time range.

    Args:
        region: An AvalancheRegion object
        representing the region for which to retrieve avalanche data.
        start_date: A string representing
        the start date of the time range in the format "YYYY-MM-DD".
        end_date: A string representing the end
         date of the time range in the format "YYYY-MM-DD".
services.scraper.
    Returns:
        A list of VarsomAvalancheResponse objects
         representing the retrieved avalanche warnings.

    Raises:
        ValueError: If the response from Varsom's API
        does not match the expected format.
        RequestException: If an unexpected error
         occurs during the avalanche data fetching process.
    """

    url = generate_url(region.region_id, start_date, end_date)
    print("Using url: " + url)

    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    response = requests.get(url, headers=headers, timeout=60 * 10)

    if response.status_code == requests.codes.ok:  # pylint: disable=E1101
        try:
            parsed: List[Dict[str, Any]] = response.json()
            warnings: List[VarsomAvalancheResponse] = [
                VarsomAvalancheResponse(**data) for data in parsed
            ]
            return warnings
        except Exception as err:
            raise ValueError(
                f"The response we received "
                f"from Varsom's API did not match what we expected: {err}"
            ) from err
    else:
        raise RequestException(
            f"Uh oh! Something unexpected happened during avalanche fetching: {response}"
        )


def generate_url(region_id: str, start_date: str, end_date: str) -> str:
    """
    Generate the URL for retrieving avalanche data
    from Varsom's API.

    Args:
        region_id: A string representing the region
        ID for which to retrieve avalanche data.
        start_date: A string representing the start date
        of the time range in the format "YYYY-MM-DD".
        end_date: A string representing the end date of
         the time range in the format "YYYY-MM-DD".

    Returns:
        The URL string for retrieving avalanche data
        from Varsom's API.
    """

    language_key = "1"
    url = (
        f"https://api01.nve.no/"
        f"hydrology/forecast/avalanche/v6.2.1/api/"
        f"AvalancheWarningByRegion/Simple/"
        f"{region_id}/{language_key}/{start_date}/{end_date}"
    )
    return url


print("Hello")
