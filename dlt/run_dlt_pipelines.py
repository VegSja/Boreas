#!/usr/bin/env python3
"""
Entry point for executing the data pipeline.
"""

from pipelines.avalanche_pipeline import run_avalanche_pipeline
from pipelines.weather_pipeline import run_weather_pipeline


if __name__ == "__main__":
    print("Run weather pipeline")
    run_weather_pipeline()
    print("Run avalanche pipeline")
    run_avalanche_pipeline()