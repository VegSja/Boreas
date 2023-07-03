from typing import List

import pandas as pd

from app.services.scraper.Constants.avalanche_regions import (
    AvalancheRegion,
    AVALANCHE_REGIONS,
)
from app.services.scraper.avalanche_fetcher import get_avalanche_data
from app.services.scraper.csv_writer import (
    write_avalanche_forecast_to_csv,
    write_weather_forecast_to_csv,
)
from app.services.scraper.data_classes.avalache_data import VarsomAvalancheResponse
from app.services.scraper.data_classes.weather_data import WeatherData
from app.services.scraper.weather_fetcher import get_weather_data


class DataFetcher:
    """
    A class for fetching and saving weather and avalanche data for a given time range and region.

    Args:
        start_year: An integer representing the starting year of the data fetching period.
        end_year: An integer representing the ending year of the data fetching period.

    Methods:
        get_weather_data: Retrieve weather data for a specific region and time range.
        get_avalanche_data_for_region: Retrieve avalanche data for a specific region and time range.
        get_data_and_save: Fetch and save weather and
         avalanche data for the specified time range and regions.

    Note:
        The class uses the following files for saving the data:
        - "avalanches.csv": CSV file for storing avalanche data.
        - "weather.csv": CSV file for storing weather data.
        If the files already exist, the new data will be appended to them.

    """

    def __init__(self, start_year: int, end_year: int):
        self.start_year: int = start_year
        self.end_year: int = end_year

    def get_weather_data(
        self, region: AvalancheRegion, start_date: str, end_date: str
    ) -> WeatherData:
        """
        Retrieve weather data for a specific region and time range.

        Args:
            region: An AvalancheRegion object
            representing the region for which to retrieve weather data.
            start_date: The start date of the time range.
            end_date: The end date of the time range.

        Returns:
            A WeatherData object representing the retrieved weather forecasts.

        """

        return get_weather_data(region, start_date, end_date)

    def get_avalanche_data_for_region(
        self, region: AvalancheRegion, start_date: str, end_date: str
    ) -> List[VarsomAvalancheResponse]:
        """
        Retrieve avalanche data for a specific region and time range.

        Args:
            region: An AvalancheRegion
             object representing the region for which to retrieve avalanche data.
            start_date: The start date of the time range.
            end_date: The end date of the time range.

        Returns:
            A list of VarsomAvalancheResponse objects
             representing the retrieved avalanche warnings.

        """

        return get_avalanche_data(
            region=region, start_date=start_date, end_date=end_date
        )

    def _save_avalanche_warnings(self, warnings: List[VarsomAvalancheResponse]) -> None:
        """
        Save avalanche warnings to a CSV file.

        Args:
            warnings: A list of VarsomAvalancheResponse
             objects representing the avalanche warnings.

        Returns:
            None

        """

        write_avalanche_forecast_to_csv(warnings)

    def _save_weather_forecasts(
        self, forecasts: WeatherData, region: AvalancheRegion
    ) -> None:
        """
        Save weather forecasts to a CSV file.

        Args:
            forecasts: A WeatherData object representing the weather forecasts.
            region: An AvalancheRegion object
             representing the region for which the forecasts are generated.

        Returns:
            None

        """

        write_weather_forecast_to_csv(forecasts, region)

    def get_data_and_save(self) -> None:
        """
        Fetch and save weather and avalanche data
         for the specified time range and regions.

        Returns:
            None

        """

        pd.DataFrame(
            columns=[
                "RegId",
                "RegionId",
                "RegionName",
                "RegionTypeId",
                "RegionTypeName",
                "DangerLevel",
                "ValidFrom",
                "ValidTo",
                "NextWarningTime",
                "PublishTime",
                "DangerIncreaseTime",
                "DangerDecreaseTime",
                "MainText",
                "LangKey",
            ],
        ).to_csv("avalanches.csv", index=False)
        pd.DataFrame(
            columns=[
                "latitude",
                "longitude",
                "elevation",
                "time",
                "region_id",
                "region_name",
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "rain_sum",
                "snowfall_sum",
                "windspeed_10m_max",
                "windgusts_10m_max",
                "winddirection_10m_dominant",
            ],
        ).to_csv("weather.csv", index=False)

        for year in range(self.start_year, self.end_year):
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            for region in AVALANCHE_REGIONS:
                print(f"Region: {region}")
                print("Fetching avalanches...")
                avalanches = self.get_avalanche_data_for_region(
                    region=region, start_date=start_date, end_date=end_date
                )
                print("Saving avalanches...")
                self._save_avalanche_warnings(warnings=avalanches)
                print("Fetching weather...")
                weather = self.get_weather_data(
                    region=region, start_date=start_date, end_date=end_date
                )
                print("Saving weather...")
                self._save_weather_forecasts(forecasts=weather, region=region)


fetcher = DataFetcher(start_year=2018, end_year=2022)
fetcher.get_data_and_save()
