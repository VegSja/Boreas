from typing import List

from app.services.scraper import AvalancheFetcher, WeatherFetcher
from app.services.scraper.Constants.avalanche_regions import AvalancheRegion, AVALANCHE_REGIONS
from app.services.scraper.csv_writer import write_avalanche_forecast_to_csv, write_weather_forecast_to_csv
from app.services.scraper.data_classes.avalache_data import VarsomAvalancheResponse
from app.services.scraper.data_classes.weather_data import WeatherData

REGION_ID_AVALANCHE = "3022"  # Trollheimen
START_DATE = "2023-05-30"
END_DATE = "2023-05-31"

LAT = 62.8000
LON = 9.1999

class DataFetcher:
    def __init__(self, START_DATE: str, END_DATE: str):
        self.START_DATE: str = START_DATE
        self.END_DATE: str = END_DATE

    def _get_weather_data(self, region: AvalancheRegion) -> WeatherData:
        return WeatherFetcher.get_weather_data(region, self.START_DATE, self.END_DATE)

    def _get_avalanche_data_for_region(self, region: AvalancheRegion) -> List[VarsomAvalancheResponse]:
        return AvalancheFetcher.get_avalanche_data(region=region, start_date=self.START_DATE, end_date=self.END_DATE)

    def _save_avalanche_warnings(self, warnings: List[VarsomAvalancheResponse]) -> None:
        write_avalanche_forecast_to_csv(warnings)

    def _save_weather_forecasts(self, forecasts: WeatherData, region: AvalancheRegion) -> None:
        write_weather_forecast_to_csv(forecasts, region)

    def get_data_and_save(self) -> None:
        for region in AVALANCHE_REGIONS:
            avalanches = self._get_avalanche_data_for_region(region=region)
            self._save_avalanche_warnings(warnings=avalanches)
            weather = self._get_weather_data(region=region)
            self._save_weather_forecasts(forecasts=weather, region=region)


fetcher = DataFetcher(START_DATE=START_DATE, END_DATE=END_DATE)
fetcher.get_data_and_save()

