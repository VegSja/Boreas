from typing import List
from dataclasses import dataclass


@dataclass
class WeatherData:
    latitude: float
    longitude: float
    generationtime_ms: float
    utc_offset_seconds: float
    timezone: str
    timezone_abbreviation: str
    elevation: float
    daily: "DailyData"
    daily_units: "DailyUnits"


@dataclass
class DailyUnits:
    time: str
    weathercode: str
    temperature_2m_max: str
    temperature_2m_min: str
    temperature_2m_mean: str
    rain_sum: str
    snowfall_sum: str
    precipitation_hours: str
    windspeed_10m_max: str
    windgusts_10m_max: str
    winddirection_10m_dominant: str


@dataclass
class DailyData:
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    temperature_2m_mean: List[float]
    rain_sum: List[float]
    snowfall_sum: List[float]
    windspeed_10m_max: List[float]
    windgusts_10m_max: List[float]
    winddirection_10m_dominant: List[float]
    weathercode: List[str]
    precipitation_hours: List[float]
