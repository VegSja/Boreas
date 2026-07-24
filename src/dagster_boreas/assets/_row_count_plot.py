"""Helper for embedding a rows-per-date line chart in asset metadata.

Renders a compact matplotlib line chart of ``COUNT(*) GROUP BY <date_col>``
and returns it as a ``dg.MetadataValue.md`` so it displays inline on the
materialization page in the Dagster UI. Failures are swallowed to a text
value — metadata rendering must never fail a run.
"""

from __future__ import annotations

import base64
import io

import dagster as dg
import matplotlib

matplotlib.use("Agg")  # headless — must be set before pyplot import
import matplotlib.pyplot as plt  # noqa: E402
from dagster_duckdb import DuckDBResource  # noqa: E402


def rows_per_date_plot(
    duckdb: DuckDBResource,
    *,
    schema: str,
    table: str,
    date_column: str,
    title: str | None = None,
) -> dg.MetadataValue:
    """Return a MetadataValue containing a base64-embedded PNG line chart of
    row count per value of ``date_column`` in ``"<schema>"."<table>"``.

    Casts the date column to DATE so timestamps collapse to daily buckets.
    """
    qualified = f'"{schema}"."{table}"'
    try:
        with duckdb.get_connection() as con:
            rows = con.execute(
                f'SELECT CAST("{date_column}" AS DATE) AS d, COUNT(*) AS n '
                f"FROM {qualified} "
                f'WHERE "{date_column}" IS NOT NULL '
                f"GROUP BY d ORDER BY d"
            ).fetchall()
        if not rows:
            return dg.MetadataValue.md("_No rows to plot._")

        dates = [r[0] for r in rows]
        counts = [r[1] for r in rows]

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(dates, counts, marker="o", markersize=2, linewidth=1)
        ax.set_title(title or f"Rows per {date_column} — {schema}.{table}")
        ax.set_xlabel(date_column)
        ax.set_ylabel("row count")
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.autofmt_xdate()
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110)
        plt.close(fig)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return dg.MetadataValue.md(f"![rows per {date_column}](data:image/png;base64,{encoded})")
    except Exception as exc:  # pragma: no cover - metadata must never fail the run
        return dg.MetadataValue.text(f"plot_error: {type(exc).__name__}: {exc}")
