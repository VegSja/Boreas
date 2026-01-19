from pathlib import Path
from typing import Any, Mapping, Optional

from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets

PROJECT_ROOT = Path(__file__).parent.parent.parent
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_boreas"

dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    packaged_project_dir=DBT_PROJECT_DIR,
)

dbt_project.prepare_if_dev()


# Map dbt source tables to DLT asset names
SOURCE_TO_DLT_ASSET: dict[tuple[str, str], str] = {
    # (source_name, table_name) -> dlt_asset_name
    ("1_bronze", "avalanche_regions"): "regions_bronze",
    ("1_bronze", "avalanche_danger_levels"): "avalanche_bronze",
    ("1_bronze", "weather_grids"): "weather_grids_bronze",
    ("1_bronze", "weather_historic"): "weather_historic_bronze",
    ("1_bronze", "weather_forecast"): "weather_forecast_bronze",
}


class DltDbtTranslator(DagsterDbtTranslator):
    """Custom translator to connect dbt sources to DLT assets."""

    def get_asset_key(self, dbt_resource_props: Mapping[str, Any]) -> AssetKey:
        """Map dbt sources to their upstream DLT asset keys."""
        resource_type = dbt_resource_props.get("resource_type")

        if resource_type == "source":
            source_name = dbt_resource_props.get("source_name")
            table_name = dbt_resource_props.get("name")

            # Look up the DLT asset name for this source
            dlt_asset_name = SOURCE_TO_DLT_ASSET.get((source_name, table_name))
            if dlt_asset_name:
                return AssetKey(dlt_asset_name)

        # Default behavior for models and other resources
        return super().get_asset_key(dbt_resource_props)


@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project,
    dagster_dbt_translator=DltDbtTranslator(),
)
def dbt_boreas_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    """Run dbt models as Dagster assets."""
    yield from dbt.cli(["build"], context=context).stream()


dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,  # profiles.yml 
)