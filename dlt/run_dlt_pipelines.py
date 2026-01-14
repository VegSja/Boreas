#!/usr/bin/env python3
"""
Weather Pipeline Runner

Entry point for executing the weather data pipeline.
"""

from pipelines.weather_pipeline import run_weather_pipeline


if __name__ == "__main__":
    print("Run weather pipeline")
    run_weather_pipeline()