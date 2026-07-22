"""Dagster asset that builds the Evidence.dev static dashboard.

Depends on both gold-layer dbt models so a full-graph materialization
(or the daily schedule) refreshes the site automatically after the
underlying tables are rebuilt.

Requires ``node`` + ``npm`` on the host. Run ``npm install`` inside
``evidence/`` once before the first materialization.
"""

import os
import shutil
import subprocess
from pathlib import Path

import dagster as dg
from dagster import AssetExecutionContext

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = REPO_ROOT / "evidence"
DUCKDB_PATH = REPO_ROOT / "boreas.duckdb"

GOLD_DEPS = [
    dg.AssetKey(["3_gold", "avalanche_per_region"]),
    dg.AssetKey(["3_gold", "weather_per_region"]),
]


def _run(cmd: list[str], cwd: Path, env: dict[str, str], log) -> None:
    log.info(f"$ {' '.join(cmd)}  (cwd={cwd})")
    proc = subprocess.run(
        cmd, cwd=cwd, env=env, capture_output=True, text=True, check=False
    )
    if proc.stdout:
        log.info(proc.stdout)
    if proc.stderr:
        log.info(proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{' '.join(cmd)} failed with exit code {proc.returncode}"
        )


@dg.asset(
    key=dg.AssetKey(["4_reporting", "evidence_dashboard"]),
    deps=GOLD_DEPS,
    compute_kind="evidence",
    group_name="reporting",
    description=(
        "Static Evidence.dev site built from the gold-layer DuckDB tables. "
        "Output written to evidence/build/."
    ),
)
def evidence_dashboard(context: AssetExecutionContext) -> dg.MaterializeResult:
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError(
            "npm not found on PATH. Install Node.js (>=18) to build the "
            "Evidence dashboard, or exclude the '4_reporting/*' asset "
            "selection from the run."
        )

    if not (EVIDENCE_DIR / "node_modules").exists():
        _run([npm, "install"], EVIDENCE_DIR, os.environ.copy(), context.log)

    env = os.environ.copy()
    # Evidence resolves this path from sources/boreas/, so compute a relative
    # path back to the DuckDB file at the repo root.
    env["EVIDENCE_SOURCE__boreas__filename"] = "../../../boreas.duckdb"

    _run([npm, "run", "sources"], EVIDENCE_DIR, env, context.log)
    _run([npm, "run", "build"], EVIDENCE_DIR, env, context.log)

    build_dir = EVIDENCE_DIR / "build"
    return dg.MaterializeResult(
        metadata={
            "build_dir": dg.MetadataValue.path(str(build_dir)),
            "duckdb_path": dg.MetadataValue.path(str(DUCKDB_PATH)),
            "pages": dg.MetadataValue.md(
                "- [index](index.html)\n- [avalanche](avalanche/index.html)\n"
                "- [weather](weather/index.html)"
            ),
        }
    )
