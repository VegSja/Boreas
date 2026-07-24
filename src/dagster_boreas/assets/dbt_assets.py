"""Dagster assets for the dbt_boreas project.

Loads every dbt model in ``dbt_boreas/`` as a Dagster asset. Bronze-layer
sources declared in the dbt project match the AssetKeys produced by
``dagster_boreas.assets.dlt_assets`` so the full graph
(dlt -> silver -> gold) is auto-wired.
"""

from pathlib import Path
from typing import Any, Mapping, NamedTuple

import dagster as dg
from dagster import AssetExecutionContext
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets
from dagster_duckdb import DuckDBResource

from src.dagster_boreas.assets._row_count_plot import rows_per_date_plot

REPO_ROOT = Path(__file__).resolve().parents[3]
DBT_PROJECT_DIR = REPO_ROOT / "dbt_boreas"

dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,
    target="dev",
)
if not dbt_project.manifest_path.exists():
    dbt_project.prepare_if_dev()

dbt_resource = DbtCliResource(project_dir=dbt_project)


class BoreasDbtTranslator(DagsterDbtTranslator):
    """Route every node from the ``elementary`` dbt package into a dedicated
    ``observability`` group so the ~30 metadata models don't clutter the
    bronze/silver/gold lineage."""

    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> str | None:
        if dbt_resource_props.get("package_name") == "elementary":
            return "observability"
        return super().get_group_name(dbt_resource_props)


class _DatePlotSpec(NamedTuple):
    schema: str
    table: str
    date_column: str


_ROWS_PER_DATE_MODELS: dict[str, _DatePlotSpec] = {
    "fact_weather": _DatePlotSpec("2_silver", "fact_weather", "time"),
    "fact_avalanche_danger": _DatePlotSpec("2_silver", "fact_avalanche_danger", "valid_from"),
    "avalanche_per_region": _DatePlotSpec("3_gold", "avalanche_per_region", "date"),
    "weather_per_region": _DatePlotSpec("3_gold", "weather_per_region", "date"),
}


@dbt_assets(manifest=dbt_project.manifest_path, dagster_dbt_translator=BoreasDbtTranslator())
def dbt_boreas_assets(
    context: AssetExecutionContext, dbt: DbtCliResource, duckdb: DuckDBResource
):
    for event in dbt.cli(["build"], context=context).stream():
        yield event
        output_name = getattr(event, "output_name", None)
        spec = _ROWS_PER_DATE_MODELS.get(output_name) if output_name else None
        if spec is None:
            continue
        context.add_output_metadata(
            metadata={
                "rows_per_date": rows_per_date_plot(
                    duckdb,
                    schema=spec.schema,
                    table=spec.table,
                    date_column=spec.date_column,
                )
            },
            output_name=output_name,
        )
