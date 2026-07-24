"""Dagster assets for the dbt_boreas project.

Loads every dbt model in ``dbt_boreas/`` as a Dagster asset. Bronze-layer
sources declared in the dbt project match the AssetKeys produced by
``dagster_boreas.assets.dlt_assets`` so the full graph
(dlt -> silver -> gold) is auto-wired.
"""

from pathlib import Path
from typing import Any, Mapping

import dagster as dg
from dagster import AssetExecutionContext
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, DbtProject, dbt_assets

REPO_ROOT = Path(__file__).resolve().parents[3]
DBT_PROJECT_DIR = REPO_ROOT / "dbt_boreas"

dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,
    target="dev",
)
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


@dbt_assets(manifest=dbt_project.manifest_path, dagster_dbt_translator=BoreasDbtTranslator())
def dbt_boreas_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
