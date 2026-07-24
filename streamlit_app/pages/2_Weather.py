"""Weather detail page."""

from __future__ import annotations

import time

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

from Home import WX, _bbox_polygon, query

st.set_page_config(page_title="Weather detail", layout="wide")
st.title("Weather detail")

_raw_dates = query(f"select distinct date::date as d from {WX} order by d desc")["d"].tolist()
dates = [d.date() if hasattr(d, "date") else d for d in _raw_dates]
if not dates:
    st.warning("No weather data available.")
    st.stop()

st.subheader("31-day national map — drag or play to animate")

NAT_VARS: dict[str, tuple[str, str]] = {
    "average_temperature": ("Avg temperature (°C)", "temperature"),
    "max_snowfall": ("Max snowfall (mm)", "snowfall"),
    "max_rain": ("Max rain (mm)", "rain"),
    "max_snow_depth": ("Max snow depth (cm)", "snow"),
    "max_windspeed": ("Max wind (m/s)", "wind"),
}

nat_var = st.selectbox(
    "Variable",
    options=list(NAT_VARS.keys()),
    format_func=lambda k: NAT_VARS[k][0],
    key="nat_anim_var",
)

nat_end = st.selectbox("End date", options=sorted(dates, reverse=True), index=0)
# Last 31 *available* dates up to end_date — WX ingestion has gaps and a plain
# calendar window would collapse to a handful of days.
recent_dates = sorted([d for d in dates if d <= nat_end], reverse=True)[:31]
nat_start = min(recent_dates)

nat_cells = query(
    f"""
    select
        date::date as date,
        east_south_lat, east_south_lon, west_north_lat, west_north_lon,
        {nat_var} as value
    from {WX}
    where date::date in ({",".join(["?"] * len(recent_dates))})
    """,
    tuple(recent_dates),
)

if nat_cells.empty:
    st.info("No weather data in the last 31 days.")
else:
    nat_cells["date"] = pd.to_datetime(nat_cells["date"]).dt.date
    nat_days = sorted(nat_cells["date"].unique())
    nvmin = float(nat_cells["value"].min())
    nvmax = float(nat_cells["value"].max())
    nspan = max(nvmax - nvmin, 1e-6)
    nat_label = NAT_VARS[nat_var][0]

    # Precompute polygons + colours once for the whole window so fragment ticks
    # only mask by date instead of running .apply per row per frame.
    nat_cells = nat_cells.dropna(subset=["value"]).copy()
    nat_cells["polygon"] = nat_cells.apply(_bbox_polygon, axis=1)
    _f = ((nat_cells["value"] - nvmin) / nspan).clip(0, 1)
    nat_cells["color"] = [
        [int(255 * f), 64, int(255 * (1 - f)), 180] for f in _f.tolist()
    ]

    @st.fragment
    def _animated_national_map() -> None:
        # Reset frame when window/variable changes to avoid stale index into a shorter list.
        nat_key = f"{nat_end}|{nat_var}|{len(nat_days)}"
        if st.session_state.get("_nat_key") != nat_key:
            st.session_state["_nat_key"] = nat_key
            st.session_state["_nat_idx"] = len(nat_days) - 1
            st.session_state["_nat_play"] = False

        playing = st.session_state["_nat_play"]
        nc1, nc2, nc3 = st.columns([1, 1, 3])
        if nc1.button("⏸ Pause" if playing else "▶ Play", key="nat_play_btn"):
            st.session_state["_nat_play"] = not playing
            st.rerun(scope="fragment")
        nat_speed = nc2.selectbox("Speed", ["0.3s", "0.6s", "1.0s"], index=1, label_visibility="collapsed", key="nat_speed")
        slider_val = nc3.slider(
            f"Day  ·  {nat_start} → {nat_end}",
            min_value=0,
            max_value=len(nat_days) - 1,
            value=st.session_state["_nat_idx"],
            format="",
            key="nat_slider",
        )
        # Slider drives idx only when paused; during playback the loop owns it.
        if not playing:
            st.session_state["_nat_idx"] = slider_val

        metric_slot = st.empty()
        map_slot = st.empty()
        st.caption(
            f"Colour scale is fixed across the full 31-day window "
            f"({nvmin:.1f} → {nvmax:.1f}), so cells stay comparable as you scrub."
        )

        def _render(idx: int) -> None:
            day = nat_days[idx]
            slice_ = nat_cells[nat_cells["date"] == day]
            with metric_slot.container():
                m1, m2 = st.columns(2)
                m1.metric("Date", day.strftime("%Y-%m-%d"))
                m2.metric(
                    f"{nat_label} (national avg)",
                    f"{slice_['value'].mean():.1f}" if not slice_.empty else "—",
                )
            map_slot.pydeck_chart(
                pdk.Deck(
                    map_style="light",
                    initial_view_state=pdk.ViewState(latitude=65, longitude=15, zoom=3.5),
                    layers=[
                        pdk.Layer(
                            "PolygonLayer",
                            data=slice_,
                            get_polygon="polygon",
                            get_fill_color="color",
                            get_line_color=[80, 80, 80],
                            line_width_min_pixels=0.3,
                            pickable=True,
                            stroked=True,
                            filled=True,
                            opacity=0.7,
                        )
                    ],
                    tooltip={"text": f"{nat_label}: {{value}}"},
                )
            )

        if playing:
            delay = {"0.3s": 0.3, "0.6s": 0.6, "1.0s": 1.0}[nat_speed]
            while st.session_state["_nat_play"]:
                idx = st.session_state["_nat_idx"]
                _render(idx)
                time.sleep(delay)
                st.session_state["_nat_idx"] = (idx + 1) % len(nat_days)
        else:
            _render(st.session_state["_nat_idx"])

    _animated_national_map()

st.subheader("Trends (all regions, daily aggregate)")
trend = query(
    f"""
    select date::date as date,
           avg(average_temperature) as avg_temp,
           avg(max_snowfall)        as avg_max_snowfall,
           avg(max_rain)            as avg_max_rain,
           avg(max_snow_depth)      as avg_max_snow_depth,
           avg(max_windspeed)       as avg_max_wind
    from {WX}
    group by 1
    order by 1
    """
)
if not trend.empty:
    st.altair_chart(
        alt.Chart(trend).mark_line().encode(x="date:T", y=alt.Y("avg_temp:Q", title="°C"))
        .properties(title="Average temperature", height=280),
        use_container_width=True,
    )
    grid = [
        ("avg_max_snowfall", "Max snowfall (mm)"),
        ("avg_max_rain", "Max rain (mm)"),
        ("avg_max_snow_depth", "Max snow depth (cm)"),
        ("avg_max_wind", "Max wind (m/s)"),
    ]
    row1, row2 = st.columns(2), st.columns(2)
    for (field, title), slot in zip(grid, [*row1, *row2]):
        slot.altair_chart(
            alt.Chart(trend).mark_line().encode(x="date:T", y=alt.Y(f"{field}:Q", title=title))
            .properties(title=title, height=220),
            use_container_width=True,
        )

st.subheader("Recent records")
recent = query(f"select * from {WX} order by date desc limit 200")
st.dataframe(recent, use_container_width=True, hide_index=True)
