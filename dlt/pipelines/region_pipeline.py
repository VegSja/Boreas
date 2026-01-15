import dlt
import os
from sources.regions.region_source import regions_source


def create_region_pipeline():
    # Get absolute path to project root (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'boreas')
    
    pipeline = dlt.pipeline(
        pipeline_name="region_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name=db_path,
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='enlighten'
    )
    return pipeline


def run_regions_pipeline():
    pipeline = create_region_pipeline()
    pipeline.run(regions_source())