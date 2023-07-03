from typing import Dict, Any
import requests
from requests.exceptions import RequestException


from app.services.scraper.Constants.avalanche_regions import AvalancheRegion
from app.services.scraper.data_classes.weather_data import (
    WeatherData,
    DailyData,
    DailyUnits,
)


def from_nested_dict(dict_input: Dict[str, Any]) -> Any:
    """Converts a nested dictionary into the
     appropriate data structure based on the "__type__" field.

    Args:
        dict_input (Dict[str, Any]): The input dictionary to be converted.

    Returns:
        Any: The converted nested data structure
         based on the "__type__" field in the input dictionary.
    """
    if "__type__" in dict_input:
        type_name = dict_input.pop("__type__")
        if type_name == "WeatherData":
            dict_input["daily"] = DailyData(**dict_input["daily"])
            dict_input["daily_units"] = DailyUnits(**dict_input["daily_units"])
            return WeatherData(**dict_input)
        if type_name == "DailyData":
            return DailyData(**dict_input)
        if type_name == "DailyUnits":
            return DailyUnits(**dict_input)
    return dict_input


def dict_to_weatherdata(parsed_data: Dict[str, Any]) -> WeatherData:
    """Converts a parsed data dictionary into a WeatherData object.

    Args:
        parsed_data (Dict[str, Any]): The parsed data
         dictionary containing the necessary fields for creating a WeatherData object.

    Returns:
        WeatherData: The created WeatherData object.
    """
    daily_data: DailyData = DailyData(**parsed_data["daily"])
    daily_units: DailyUnits = DailyUnits(**parsed_data["daily_units"])
    weather = WeatherData(
        latitude=parsed_data["latitude"],
        longitude=parsed_data["longitude"],
        generationtime_ms=parsed_data["generationtime_ms"],
        utc_offset_seconds=parsed_data["utc_offset_seconds"],
        timezone=parsed_data["timezone"],
        timezone_abbreviation=parsed_data["timezone_abbreviation"],
        elevation=parsed_data["elevation"],
        daily=daily_data,
        daily_units=daily_units,
    )
    return weather


def get_weather_data(
        region: AvalancheRegion, start_date: str, end_date: str
) -> WeatherData:
    """Retrieves weather data for a specific region, start date, and end date.

    Args:
        region (AvalancheRegion): The region for which weather data is requested.
        start_date (str): The start date of the desired weather data range.
        end_date (str): The end date of the desired weather data range.

    Returns:
        WeatherData: The retrieved WeatherData object
        for the specified region and date range.

    Raises:
        RequestException: If the request for weather data fails.
        ValueError: If there is an error parsing the API response for weather data.
    """
    url = generate_url(region.lat, region.lon, start_date, end_date)

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except RequestException as err:
        raise RequestException(
            f"The request for weather data failed: {err}"
        ) from err

    try:
        res: Dict[str, Any] = response.json()
        weather = dict_to_weatherdata(res)
        return weather
    except Exception as err:
        raise ValueError(
            f"Failed to parse API response for weather data: {err}"
        ) from err


def generate_url(
        latitude: float, longitude: float, start_date: str, end_date: str
) -> str:
    """Generates a URL for retrieving weather data.

    Args:
        latitude (float): The latitude of the location for which weather data is requested.
        longitude (float): The longitude of the location for which weather data is requested.
        start_date (str): The start date of the desired weather data range.
        end_date (str): The end date of the desired weather data range.

    Returns:
        str: The generated URL for retrieving weather data.
    """
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=" \
          f"{latitude:.4f}&longitude={longitude:.4f}&" \
          f"start_date={start_date}&" \
          f"end_date={end_date}&" \
          f"daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean" \
          f",rain_sum,snowfall_sum,precipitation_hours,windspeed_10m_max,windgusts_10m_max" \
          f",winddirection_10m_dominant&timezone=Europe%2FBerlin"
    return url
