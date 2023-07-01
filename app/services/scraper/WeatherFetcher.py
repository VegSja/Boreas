import json

import requests
from requests.exceptions import RequestException

from typing import Union, Dict, Any

from app.services.scraper.Constants.avalanche_regions import AvalancheRegion
from app.services.scraper.data_classes.weather_data import WeatherData, DailyData, DailyUnits


class WeatherFetcherError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

# Custom object hook function to convert nested dictionaries to data classes
def from_nested_dict(d):
    if '__type__' in d:
        type_name = d.pop('__type__')
        if type_name == 'WeatherData':
            d['daily'] = DailyData(**d['daily'])
            d['daily_units'] = DailyUnits(**d['daily_units'])
            return WeatherData(**d)
        elif type_name == 'DailyData':
            return DailyData(**d)
        elif type_name == 'DailyUnits':
            return DailyUnits(**d)
    return d


def dict_to_weatherdata(parsed_data: Dict[str, Any]) -> WeatherData:
    daily_data: DailyData = DailyData(**parsed_data["daily"])
    daily_units: DailyUnits = DailyData(**parsed_data["daily_units"])
    weather = WeatherData(
        latitude=parsed_data['latitude'],
        longitude=parsed_data['longitude'],
        generationtime_ms=parsed_data['generationtime_ms'],
        utc_offset_seconds=parsed_data['utc_offset_seconds'],
        timezone=parsed_data['timezone'],
        timezone_abbreviation=parsed_data['timezone_abbreviation'],
        elevation=parsed_data['elevation'],
        daily=daily_data,
        daily_units=daily_units,
    )
    return weather


def get_weather_data(region: AvalancheRegion, start_date: str, end_date: str) -> WeatherData:
    url = generate_url(region.lat, region.lon, start_date, end_date)

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except RequestException as err:
        raise RequestException(f"The request for weatherdata failed: {err}")

    try:
        res: Dict[str, Any] = response.json()
        weather = dict_to_weatherdata(res)
        return weather
    except Exception as err:
        raise(ValueError(f"Failed to parse API response for weather: {err}"))


def generate_url(latitude: float, longitude: float, start_date: str, end_date: str) -> str:
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude:.4f}&longitude={longitude:.4f}&start_date={start_date}&end_date={end_date}&daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean,rain_sum,snowfall_sum,precipitation_hours,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant&timezone=Europe%2FBerlin"
    return url
