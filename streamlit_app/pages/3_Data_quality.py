"""Elementary data-quality report embedded from evidence/elementary/index.html."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

REPORT_PATH = Path(__file__).resolve().parent.parent / "static" / "evidence" / "elementary" / "index.html"
REPORT_URL = "/static/evidence/elementary/index.html"


def main() -> None:
    st.set_page_config(page_title="Boreas — Data quality", layout="wide")
    st.title("Data quality — Elementary report")

    if not REPORT_PATH.exists():
        st.warning(
            f"No Elementary report found at `{REPORT_PATH}`.\n\n"
            "Materialize the `4_reporting/elementary_report` asset in Dagster "
            "(or run `edr report` from `dbt_boreas/`) to generate it."
        )
        return

    st.link_button("Open full report in new tab ↗", REPORT_URL, type="primary")
    components.iframe(REPORT_URL, height=1600, scrolling=True)


if __name__ == "__main__":
    main()
