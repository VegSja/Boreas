#!/usr/bin/env python3
"""
Entry point for executing the data pipeline.
"""

import sys
from pipelines.avalanche_pipeline import run_avalanche_pipeline
from dlt.pipelines.weather_forecast_pipeline import run_weather_forecast_pipeline
from dlt.pipelines.weather_historic_pipeline import run_weather_historic_pipeline
from pipelines.region_pipeline import run_regions_pipeline
from utils.logging import setup_logger

logger = setup_logger(__name__)


def main():
    pipelines = [
        ("regions", run_regions_pipeline),
        ("weather_historic", run_weather_historic_pipeline),
        ("weather_forcast", run_weather_forecast_pipeline),
        ("avalanche", run_avalanche_pipeline),
    ]
    
    failures = []
    
    for name, run_fn in pipelines:
        logger.info(f"Starting {name} pipeline")
        try:
            run_fn()
            logger.info(f"Completed {name} pipeline successfully")
        except Exception as e:
            logger.error(f"Pipeline {name} failed: {e}")
            failures.append((name, e))
    
    if failures:
        logger.error(f"{len(failures)} pipeline(s) failed: {[f[0] for f in failures]}")
        sys.exit(1)
    
    logger.info("All pipelines completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()