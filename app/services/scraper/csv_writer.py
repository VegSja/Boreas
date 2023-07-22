from typing import List

import pandas as pd

from Constants.avalanche_regions import AvalancheRegion
from data_classes.avalache_data import VarsomAvalancheResponse
from data_classes.weather_data import WeatherData


def write_avalanche_forecast_to_csv(forecasts: List[VarsomAvalancheResponse]) -> None:
    """
    Write avalanche forecasts to a CSV file.

    Args:
        forecasts: A list of VarsomAvalancheResponse
         objects representing the avalanche forecasts.

    Note:
        The function appends the forecasts
        to an existing CSV file named "avalanches.csv".
        If the file doesn't exist, it will be created.

    Returns:
        None
    """

    rows = []
    for forecast in forecasts:
        rows.append(forecast)
    df = pd.DataFrame(rows)
    df.to_csv("avalanches.csv", index=False, mode="a", header=False)


def write_weather_forecast_to_csv(
    forecasts: WeatherData, region: AvalancheRegion
) -> None:
    """
    Write weather forecasts to a CSV file.

    Args:
        forecasts: A WeatherData object
        representing the weather forecasts.
        region: An AvalancheRegion object
        representing the region for which the forecasts are generated.

    Note:
        The function appends the forecasts
         to an existing CSV file named "weather.csv".
        If the file doesn't exist, it will be created.

    Returns:
        None
    """

    latitude = forecasts.latitude
    longitude = forecasts.longitude
    elevation = forecasts.elevation

    rows = []
    for i in range(len(forecasts.daily.time)):  # pylint: disable=C0200
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
    df.to_csv("weather.csv", index=False, mode="a", header=False)
