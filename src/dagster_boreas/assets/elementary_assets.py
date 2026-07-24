"""Dagster asset that generates the Elementary data-observability HTML report.

Runs after the gold-layer dbt models (which is where anomaly + volume tests
live). Elementary reads its own metadata schema (``elementary`` in
``boreas.duckdb``), which is populated as a side-effect of every ``dbt build``
run via the ``elementary`` package's on-run-end hook.

Writes a single self-contained ``index.html`` into ``evidence/elementary/``
(deliberately NOT ``evidence/build/`` so the file survives ``npm run build``
inside the Evidence Docker image, where it is then copied to
``/usr/share/nginx/html/elementary/`` for serving at ``/elementary/``).
"""

import os
import subprocess
from pathlib import Path

import dagster as dg
from dagster import AssetExecutionContext

REPO_ROOT = Path(__file__).resolve().parents[3]
DBT_PROJECT_DIR = REPO_ROOT / "dbt_boreas"
DUCKDB_PATH = REPO_ROOT / "boreas.duckdb"
REPORT_DIR = REPO_ROOT / "evidence" / "elementary"

GOLD_DEPS = [
    dg.AssetKey(["3_gold", "avalanche_per_region"]),
    dg.AssetKey(["3_gold", "weather_per_region"]),
]


@dg.asset(
    key=dg.AssetKey(["4_reporting", "elementary_report"]),
    deps=GOLD_DEPS,
    compute_kind="elementary",
    group_name="reporting",
    description=(
        "Elementary data-observability report (single HTML). Reads test "
        "results, freshness, and anomaly metrics from the `elementary` "
        "schema in boreas.duckdb. Served in the nginx container at "
        "/elementary/."
    ),
)
def elementary_report(context: AssetExecutionContext) -> dg.MaterializeResult:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "index.html"

    env = os.environ.copy()
    # edr runs its bundled dbt project with CWD inside .venv/, so the
    # elementary profile's relative `path:` would resolve to a rogue empty
    # DuckDB file. Force an absolute path via env var (see profiles.yml).
    env["BOREAS_DUCKDB_PATH"] = str(DUCKDB_PATH)

    cmd = [
        "uv", "run", "edr", "report",
        "--project-dir", str(DBT_PROJECT_DIR),
        "--profiles-dir", str(DBT_PROJECT_DIR),
        "--file-path", str(report_path),
        "--open-browser", "false",
        "--disable-samples", "true",
    ]
    context.log.info(f"$ {' '.join(cmd)}")
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False
    )
    if proc.stdout:
        context.log.info(proc.stdout)
    if proc.stderr:
        context.log.info(proc.stderr)
    if proc.returncode != 0 or not report_path.exists():
        raise RuntimeError(
            f"edr report failed with exit code {proc.returncode}"
        )

    size_kb = report_path.stat().st_size // 1024
    return dg.MaterializeResult(
        metadata={
            "report_path": dg.MetadataValue.path(str(report_path)),
            "size_kb": dg.MetadataValue.int(size_kb),
            "served_at": dg.MetadataValue.md(
                "In Docker: `http://localhost:8080/elementary/`"
            ),
        }
    )
