import dlt
from sources.avalanche.avalache_warnings import avalanche_warning_source


def create_avalanche_pipeline():
    pipeline = dlt.pipeline(
        pipeline_name="avalanche_pipeline",
        destination=dlt.destinations.duckdb(
            destination_name='boreas',
            enable_dataset_name_normalization=False
        ),
        dataset_name="1_bronze",
        progress='enlighten'
    )
    return pipeline


def run_avalanche_pipeline():
    pipeline = create_avalanche_pipeline()
    pipeline.run(avalanche_warning_source())