#!/usr/bin/env python
"""Sync all pipeline states from DuckDB database."""

import os
import dlt

# Get absolute path to project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, "boreas")

PIPELINES = [
    "avalanche_pipeline",
    "region_pipeline",
    "weather_forecast_pipeline",
    "weather_historic_pipeline",
    "kodd"
]


def sync_all_pipelines():
    for pipeline_name in PIPELINES:
        print(f"Syncing {pipeline_name}...")
        try:
            pipeline = dlt.pipeline(
                pipeline_name=pipeline_name,
                destination=dlt.destinations.duckdb(
                    destination_name=db_path, enable_dataset_name_normalization=False
                ),
                dataset_name="1_bronze",
            )
            pipeline.sync_destination()
            print(f"  ✓ {pipeline_name} synced")
        except Exception as e:
            print(f"  ✗ {pipeline_name} failed: {e}")


if __name__ == "__main__":
    sync_all_pipelines()
    print("\nDone! Run 'uv run dlt pipeline --list-pipelines' to see synced state.")
