"""DuckDB resource shared by dagster assets that need direct query access.

The dlt pipelines and dbt project both write to ``boreas.duckdb`` at the repo
root. This resource exposes the same file for ad-hoc query assets, sensors,
or asset checks.
"""

from __future__ import annotations

from pathlib import Path

from dagster_duckdb import DuckDBResource

REPO_ROOT = Path(__file__).resolve().parents[3]
DUCKDB_PATH = REPO_ROOT / "boreas.duckdb"

duckdb_resource = DuckDBResource(database=str(DUCKDB_PATH))
