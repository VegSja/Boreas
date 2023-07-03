from dataclasses import asdict
from typing import List

import pandas as pd

from app.services.scraper.Constants.avalanche_regions import AvalancheRegion
from app.services.scraper.data_classes.avalache_data import VarsomAvalancheResponse
from app.services.scraper.data_classes.weather_data import WeatherData


def write_avalanche_forecast_to_csv(forecasts: List[VarsomAvalancheResponse]) -> None:
    rows = []
    for forecast in forecasts:
        rows.append(forecast)
    df = pd.DataFrame(rows)
    df.to_csv("avalanches.csv", index=False, mode='a', header=False)


def write_weather_forecast_to_csv(
    forecasts: WeatherData, region: AvalancheRegion
) -> None:
    latitude = forecasts.latitude
    longitude = forecasts.longitude
    elevation = forecasts.elevation

    rows = []
    for i in range(len(forecasts.daily.time)):
        forecast = forecasts.daily
        data = {
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation,
            "time": forecast.time[i],
            "region_id": region.region_id,
            "region_name": region.name,
            "temperature_2m_max": forecast.temperature_2m_max[i],
            "temperature_2m_min": forecast.temperature_2m_min[i],
            "temperature_2m_mean": forecast.temperature_2m_mean[i],
            "rain_sum": forecast.rain_sum[i],
            "snowfall_sum": forecast.snowfall_sum[i],
            "windspeed_10m_max": forecast.windspeed_10m_max[i],
            "windgusts_10m_max": forecast.windgusts_10m_max[i],
            "winddirection_10m_dominant": forecast.winddirection_10m_dominant[i],
        }
        rows.append(data)

    df = pd.DataFrame(rows)
    df.to_csv("weather.csv", index=False, mode='a', header=False)
