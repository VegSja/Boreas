"""Dagster definitions for the Boreas ELT pipeline."""

from dagster import Definitions

from dagster_boreas.assets.dlt_assets import (
    regions_bronze,
    weather_grids_bronze,
    weather_historic_bronze,
    weather_forecast_bronze,
    avalanche_bronze,
)

defs = Definitions(
    assets=[
        regions_bronze,
        weather_grids_bronze,
        weather_historic_bronze,
        weather_forecast_bronze,
        avalanche_bronze,
    ],
)
