"""Top-level Dagster ``Definitions`` for the Boreas data platform.

Wires together:
- dlt bronze-layer ingestion assets (dlt_boreas pipelines)
- dbt silver/gold transformation assets (dbt_boreas project)
- a shared DuckDB resource
- a daily schedule that materializes the full graph
"""

from __future__ import annotations

import os
from pathlib import Path

# Point dlt at dlt_boreas/.dlt/ regardless of CWD (Dagster launches from repo root).
# Must be set before any dlt import triggers config resolution.
_DLT_PROJECT = str(Path(__file__).resolve().parents[2] / "dlt_boreas")
os.environ["DLT_PROJECT_DIR"] = _DLT_PROJECT
os.environ["DLT_CONFIG_DIR"] = str(Path(_DLT_PROJECT) / ".dlt")

import dagster as dg

from src.dagster_boreas.assets.dbt_assets import dbt_boreas_assets, dbt_resource
from src.dagster_boreas.assets.dlt_assets import dlt_bronze_assets
from src.dagster_boreas.assets.elementary_assets import elementary_report
from src.dagster_boreas.assets.evidence_assets import evidence_dashboard
from src.dagster_boreas.resources import duckdb_resource

all_assets = [*dlt_bronze_assets, dbt_boreas_assets, evidence_dashboard, elementary_report]

boreas_job = dg.define_asset_job(
    name="boreas_full_refresh",
    selection=dg.AssetSelection.all(),
    description="Materialize every dlt bronze table and every dbt model in dependency order.",
)

daily_schedule = dg.ScheduleDefinition(
    name="boreas_daily",
    job=boreas_job,
    cron_schedule="0 5 * * *",  # 05:00 Europe/Oslo local (server-time cron)
    execution_timezone="Europe/Oslo",
    default_status=dg.DefaultScheduleStatus.STOPPED,
)

defs = dg.Definitions(
    assets=all_assets,
    jobs=[boreas_job],
    schedules=[daily_schedule],
    resources={
        "dbt": dbt_resource,
        "duckdb": duckdb_resource,
    },
)
