"""Dagster assets for the dbt_boreas project.

Loads every dbt model in ``dbt_boreas/`` as a Dagster asset. Bronze-layer
sources declared in the dbt project match the AssetKeys produced by
``dagster_boreas.assets.dlt_assets`` so the full graph
(dlt -> silver -> gold) is auto-wired.
"""

from pathlib import Path

import dagster as dg
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

REPO_ROOT = Path(__file__).resolve().parents[3]
DBT_PROJECT_DIR = REPO_ROOT / "dbt_boreas"

dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
    profiles_dir=DBT_PROJECT_DIR,
    target="dev",
)
dbt_project.prepare_if_dev()

dbt_resource = DbtCliResource(project_dir=dbt_project)


@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_boreas_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
