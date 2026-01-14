import dlt
import os
from sources.avalanche.avalache_warnings import avalanche_warning_source


def create_avalanche_pipeline():
    # Get absolute path to project root (two levels up from this file)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, 'boreas')
    
    pipeline = dlt.pipeline(
        pipeline_name="avalanche_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name=db_path,
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='enlighten'
    )
    return pipeline


def run_avalanche_pipeline():
    pipeline = create_avalanche_pipeline()
    pipeline.run(avalanche_warning_source())