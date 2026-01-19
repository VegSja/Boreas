# dagster_boreas/resources/duckdb_resource.py
from pathlib import Path

from dagster_duckdb import DuckDBResource

PROJECT_ROOT = Path(__file__).parent.parent.parent
DUCKDB_PATH = PROJECT_ROOT / "boreas.duckdb"

# Simple resource configuration
duckdb_resource = DuckDBResource(
    database=str(DUCKDB_PATH),
)