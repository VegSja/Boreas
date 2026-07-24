"""Dagster assets that wrap the existing dlt bronze-layer pipelines.

Each pipeline populates one or more tables in the DuckDB ``1_bronze`` schema.
We expose them as Dagster assets keyed as ``["1_bronze", "<table>"]`` so they
line up automatically with the dbt sources declared in
``dbt_boreas/models/1_bronze/sources.yml``.

Every materialization attaches metadata describing the observed date range
(min/max of the table's time column), row count, and the dlt load id, so the
Dagster UI shows exactly which window was fetched on each run.
"""

from datetime import datetime, timezone
from typing import Iterator

import dagster as dg
from dagster import AssetExecutionContext
from dagster_duckdb import DuckDBResource

from dlt_boreas.pipelines.avalanche_pipeline import run_avalanche_pipeline
from dlt_boreas.pipelines.region_pipeline import run_regions_pipeline
from dlt_boreas.pipelines.weather_forecast_pipeline import run_weather_forecast_pipeline
from dlt_boreas.pipelines.weather_historic_pipeline import run_weather_historic_pipeline
from src.dagster_boreas.assets._row_count_plot import rows_per_date_plot

BRONZE = "1_bronze"
AVALANCHE_GROUP = "avalanche_ingestion"
WEATHER_GROUP = "weather_ingestion"
DLT_KINDS = {"dlt", "duckdb"}


def _now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


def _table_stats(
    duckdb: DuckDBResource,
    table: str,
    time_columns: tuple[str, ...] = (),
) -> dict[str, dg.MetadataValue]:
    """Read row count and (optionally) min/max of one or more time columns.

    Returns a metadata dict ready to hand to MaterializeResult. Failures are
    swallowed to a metadata note so a metadata read never fails a materialization.
    """
    meta: dict[str, dg.MetadataValue] = {}
    qualified = f'"{BRONZE}"."{table}"'
    try:
        with duckdb.get_connection() as con:
            (rows,) = con.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()
            meta["row_count"] = dg.MetadataValue.int(int(rows))
            for col in time_columns:
                row = con.execute(
                    f'SELECT MIN("{col}"), MAX("{col}") FROM {qualified}'
                ).fetchone()
                meta[f"{col}_min"] = dg.MetadataValue.text(str(row[0]) if row[0] is not None else "—")
                meta[f"{col}_max"] = dg.MetadataValue.text(str(row[1]) if row[1] is not None else "—")
    except Exception as exc:  # pragma: no cover - metadata must never fail the run
        meta["stats_error"] = dg.MetadataValue.text(f"{type(exc).__name__}: {exc}")
    return meta


def _load_info_metadata(load_info) -> dict[str, dg.MetadataValue]:
    """Extract useful fields from a dlt LoadInfo object."""
    meta: dict[str, dg.MetadataValue] = {"fetched_at": dg.MetadataValue.timestamp(_now_ts())}
    if load_info is None:
        return meta
    try:
        loads_ids = list(getattr(load_info, "loads_ids", []) or [])
        if loads_ids:
            meta["dlt_load_ids"] = dg.MetadataValue.text(", ".join(loads_ids))
        pipeline_name = getattr(load_info, "pipeline", None)
        if pipeline_name is not None:
            meta["dlt_pipeline"] = dg.MetadataValue.text(str(getattr(pipeline_name, "pipeline_name", pipeline_name)))
    except Exception as exc:  # pragma: no cover
        meta["load_info_error"] = dg.MetadataValue.text(f"{type(exc).__name__}: {exc}")
    return meta


@dg.asset(
    key=[BRONZE, "avalanche_regions"],
    group_name=AVALANCHE_GROUP,
    kinds=DLT_KINDS,
    description="Reference table of Norwegian avalanche regions loaded via dlt.",
    pool="duckdb_writer",
)
def avalanche_regions(
    context: AssetExecutionContext, duckdb: DuckDBResource
) -> dg.MaterializeResult:
    context.log.info("Running regions dlt pipeline")
    load_info = run_regions_pipeline()
    return dg.MaterializeResult(
        metadata={
            **_load_info_metadata(load_info),
            **_table_stats(duckdb, "avalanche_regions"),
        }
    )


@dg.multi_asset(
    specs=[
        dg.AssetSpec(
            key=[BRONZE, "weather_historic"],
            group_name=WEATHER_GROUP,
            kinds=DLT_KINDS,
            description="Historical weather observations loaded via dlt.",
        ),
        dg.AssetSpec(
            key=[BRONZE, "weather_grids"],
            group_name=WEATHER_GROUP,
            kinds=DLT_KINDS,
            description="Weather grid reference table loaded via dlt.",
        ),
    ],
    pool="duckdb_writer",
)
def weather_historic_bronze(
    context: AssetExecutionContext, duckdb: DuckDBResource
) -> Iterator[dg.MaterializeResult]:
    context.log.info("Running weather_historic dlt pipeline (populates weather_historic + weather_grids)")
    load_info = run_weather_historic_pipeline()
    shared = _load_info_metadata(load_info)

    yield dg.MaterializeResult(
        asset_key=dg.AssetKey([BRONZE, "weather_historic"]),
        metadata={
            **shared,
            **_table_stats(duckdb, "weather_historic", ("time",)),
            "rows_per_date": rows_per_date_plot(
                duckdb, schema=BRONZE, table="weather_historic", date_column="time"
            ),
        },
    )
    yield dg.MaterializeResult(
        asset_key=dg.AssetKey([BRONZE, "weather_grids"]),
        metadata={**shared, **_table_stats(duckdb, "weather_grids")},
    )


@dg.asset(
    key=[BRONZE, "weather_forecast"],
    group_name=WEATHER_GROUP,
    kinds=DLT_KINDS,
    description="Weather forecast data loaded via dlt. Table is fully replaced on each run.",
    pool="duckdb_writer",
)
def weather_forecast(
    context: AssetExecutionContext, duckdb: DuckDBResource
) -> dg.MaterializeResult:
    context.log.info("Running weather_forecast dlt pipeline")
    load_info = run_weather_forecast_pipeline()
    return dg.MaterializeResult(
        metadata={
            **_load_info_metadata(load_info),
            **_table_stats(duckdb, "weather_forecast", ("time",)),
            "rows_per_date": rows_per_date_plot(
                duckdb, schema=BRONZE, table="weather_forecast", date_column="time"
            ),
        }
    )


@dg.asset(
    key=[BRONZE, "avalanche_danger_levels"],
    group_name=AVALANCHE_GROUP,
    kinds=DLT_KINDS,
    description="Avalanche danger warnings loaded via dlt.",
    deps=[dg.AssetKey([BRONZE, "avalanche_regions"])],
    pool="duckdb_writer",
)
def avalanche_danger_levels(
    context: AssetExecutionContext, duckdb: DuckDBResource
) -> dg.MaterializeResult:
    context.log.info("Running avalanche dlt pipeline")
    load_info = run_avalanche_pipeline()
    return dg.MaterializeResult(
        metadata={
            **_load_info_metadata(load_info),
            **_table_stats(duckdb, "avalanche_danger_levels", ("ValidFrom", "ValidTo")),
            "rows_per_date": rows_per_date_plot(
                duckdb,
                schema=BRONZE,
                table="avalanche_danger_levels",
                date_column="ValidFrom",
            ),
        }
    )


dlt_bronze_assets = [
    avalanche_regions,
    weather_historic_bronze,
    weather_forecast,
    avalanche_danger_levels,
]
