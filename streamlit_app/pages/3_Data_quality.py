"""Elementary data-quality report, embedded from GitHub Pages."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

REPORT_URL = "https://vegsja.github.io/Boreas/"


def main() -> None:
    st.set_page_config(page_title="Boreas — Data quality", layout="wide")
    st.title("Data quality — Elementary report")
    st.link_button("Open full report in new tab ↗", REPORT_URL, type="primary")
    components.iframe(REPORT_URL, height=1600, scrolling=True)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
