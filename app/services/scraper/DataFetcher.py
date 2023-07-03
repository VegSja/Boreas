from typing import List

import pandas as pd

from app.services.scraper import AvalancheFetcher, WeatherFetcher
from app.services.scraper.Constants.avalanche_regions import (
    AvalancheRegion,
    AVALANCHE_REGIONS,
)
from app.services.scraper.csv_writer import (
    write_avalanche_forecast_to_csv,
    write_weather_forecast_to_csv,
)
from app.services.scraper.data_classes.avalache_data import VarsomAvalancheResponse
from app.services.scraper.data_classes.weather_data import WeatherData

START_DATE = "2022-05-01"
END_DATE = "2023-06-01"


class DataFetcher:
    def __init__(self, start_year: int, end_year: int):
        self.START_YEAR: int = start_year
        self.END_YEAR: int = end_year

    def _get_weather_data(self, region: AvalancheRegion, start_date, end_date) -> WeatherData:
        return WeatherFetcher.get_weather_data(region, start_date, end_date)

    def _get_avalanche_data_for_region(
        self, region: AvalancheRegion, start_date, end_date
    ) -> List[VarsomAvalancheResponse]:
        return AvalancheFetcher.get_avalanche_data(
            region=region, start_date=start_date, end_date=end_date
        )

    def _save_avalanche_warnings(self, warnings: List[VarsomAvalancheResponse]) -> None:
        write_avalanche_forecast_to_csv(warnings)

    def _save_weather_forecasts(
        self, forecasts: WeatherData, region: AvalancheRegion
    ) -> None:
        write_weather_forecast_to_csv(forecasts, region)

    def get_data_and_save(self) -> None:
        pd.DataFrame(columns=["RegId", "RegionId", "RegionName", "RegionTypeId", "RegionTypeName",
                              "DangerLevel", "ValidFrom", "ValidTo", "NextWarningTime", "PublishTime",
                              "DangerIncreaseTime", "DangerDecreaseTime", "MainText", "LangKey"],
                     ).to_csv("avalanches.csv", index=False)
        pd.DataFrame(columns= ['latitude', 'longitude', 'elevation', 'time', 'region_id', 'region_name',
                               'temperature_2m_max','temperature_2m_min', 'temperature_2m_mean',
                               'rain_sum', 'snowfall_sum', 'windspeed_10m_max','windgusts_10m_max',
                               'winddirection_10m_dominant'],
                     ).to_csv("weather.csv", index=False)

        for year in range(self.START_YEAR, self.END_YEAR):
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            for region in AVALANCHE_REGIONS:
                print(f"Region: {region}")
                print("Fetching avalanches...")
                avalanches = self._get_avalanche_data_for_region(region=region, start_date=start_date, end_date=end_date)
                print("Saving avalanches...")
                self._save_avalanche_warnings(warnings=avalanches)
                print("Fetching weather...")
                weather = self._get_weather_data(region=region, start_date=start_date, end_date=end_date)
                print("Saving weather...")
                self._save_weather_forecasts(forecasts=weather, region=region)


fetcher = DataFetcher(start_year=2018, end_year=2022)
fetcher.get_data_and_save()
