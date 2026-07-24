"""Boreas — Avalanche & Weather Streamlit dashboard."""

from __future__ import annotations

import datetime as dt
import json
import time
import urllib.request
from pathlib import Path

import duckdb
import pandas as pd
import pydeck as pdk
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "boreas.duckdb"
GEOJSON_PATH = Path(__file__).resolve().parent / "assets" / "varsom_regions.geojson"

# On Streamlit Community Cloud the repo does not contain boreas.duckdb — it
# lives on the `latest-data` GitHub release. Download it once per container.
DB_RELEASE_URL = (
    "https://github.com/VegSja/Boreas/releases/download/latest-data/boreas.duckdb"
)
if not DB_PATH.exists():
    urllib.request.urlretrieve(DB_RELEASE_URL, DB_PATH)

DANGER_COLORS: dict[int, list[int]] = {
    1: [26, 152, 80],
    2: [255, 255, 51],
    3: [253, 174, 97],
    4: [244, 109, 67],
    5: [127, 0, 0],
}


@st.cache_resource
def get_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH), read_only=True)


@st.cache_data(ttl=600)
def query(sql: str, params: tuple | None = None) -> pd.DataFrame:
    return get_conn().execute(sql, params or ()).df()


AVA = '"3_gold"."avalanche_per_region"'
WX = '"3_gold"."weather_per_region"'

# Weather cells are on a finer grid than avalanche regions. Map each weather
# cell to the avalanche region whose bbox contains its center, then average
# per (region, date). Reused by the Region monitor page.
REGION_WEATHER_CTE = f"""
with _w as (
  select date::date as date,
    (east_south_lat + west_north_lat) / 2.0 as wlat,
    (east_south_lon + west_north_lon) / 2.0 as wlon,
    max_temp, average_temperature, min_temp,
    max_snowfall, average_snowfall,
    max_rain, average_rain,
    max_snow_depth, average_snow_depth,
    max_windspeed, average_windspeed,
    average_relative_humidity
  from {WX}
),
_r as (
  select distinct region_id, region_name,
    least(east_south_lat, west_north_lat) as lat_min,
    greatest(east_south_lat, west_north_lat) as lat_max,
    least(east_south_lon, west_north_lon) as lon_min,
    greatest(east_south_lon, west_north_lon) as lon_max
  from {AVA}
),
region_weather as (
  select
    _r.region_id, _r.region_name, _w.date,
    avg(_w.max_temp)                  as max_temp,
    avg(_w.average_temperature)       as avg_temp,
    avg(_w.min_temp)                  as min_temp,
    avg(_w.max_snowfall)              as max_snowfall,
    avg(_w.average_snowfall)          as avg_snowfall,
    avg(_w.max_rain)                  as max_rain,
    avg(_w.average_rain)              as avg_rain,
    avg(_w.max_snow_depth)            as max_snow_depth,
    avg(_w.average_snow_depth)        as avg_snow_depth,
    avg(_w.max_windspeed)             as max_windspeed,
    avg(_w.average_windspeed)         as avg_windspeed,
    avg(_w.average_relative_humidity) as avg_humidity
  from _w join _r
    on _w.wlat between _r.lat_min and _r.lat_max
   and _w.wlon between _r.lon_min and _r.lon_max
  group by 1, 2, 3
)
"""


@st.cache_resource
def load_region_geojson() -> dict:
    return json.loads(GEOJSON_PATH.read_text())


def _bbox_polygon(row: pd.Series) -> list[list[float]]:
    lat_s, lon_s = row["east_south_lat"], row["east_south_lon"]
    lat_n, lon_n = row["west_north_lat"], row["west_north_lon"]
    return [
        [lon_s, lat_s],
        [lon_n, lat_s],
        [lon_n, lat_n],
        [lon_s, lat_n],
    ]


def main() -> None:
    st.set_page_config(page_title="Boreas — Avalanche & Weather", layout="wide")
    st.title("Boreas — Avalanche & Weather")

    with st.expander("About"):
        st.markdown(
            "Integrated avalanche danger and weather data across Norwegian regions. "
            "Sourced from the Norwegian Avalanche Warning Service and weather APIs, "
            "transformed through the Boreas dbt gold layer."
        )

    dates_df = query(f"select distinct date::date as d from {AVA} order by d desc")
    if dates_df.empty:
        st.warning("No avalanche data available.")
        return
    available = [d.date() if hasattr(d, "date") else d for d in dates_df["d"].tolist()]

    end_date = st.selectbox(
        "End date",
        options=available,
        index=0,
    )

    # Last 31 *available* dates up to end_date — avalanche coverage has season
    # gaps and a plain calendar window would collapse in the off-season.
    recent_dates = sorted([d for d in available if d <= end_date], reverse=True)[:31]
    anim_start, anim_end = min(recent_dates), max(recent_dates)

    warnings = query(
        f"""
        select
            date::date as date,
            region_name, region_id,
            try_cast(danger_level as integer) as danger_level,
            main_text
        from {AVA}
        where date::date in ({",".join(["?"] * len(recent_dates))})
          and try_cast(danger_level as integer) is not null
        """,
        tuple(recent_dates),
    )

    geo = load_region_geojson()
    geo_by_id = {int(f["properties"]["omradeID"]): f for f in geo["features"]}

    # Precompute one FeatureCollection per date so fragment ticks only pick from
    # a dict — no per-frame geojson walk / feature construction.
    features_by_date: dict[dt.date, dict] = {}
    for day, sub in warnings.groupby("date"):
        feats = []
        for r in sub.itertuples():
            base = geo_by_id.get(int(r.region_id))
            if base is None:
                continue
            lvl = int(r.danger_level)
            feats.append(
                {
                    "type": "Feature",
                    "geometry": base["geometry"],
                    "properties": {
                        "region_name": base["properties"].get("omradeNavn"),
                        "region_id": int(r.region_id),
                        "danger_level": lvl,
                        "main_text": r.main_text or "",
                        "fill_color": [*DANGER_COLORS.get(lvl, [128, 128, 128]), 160],
                    },
                }
            )
        day_key = day.date() if hasattr(day, "date") else day
        features_by_date[day_key] = {"type": "FeatureCollection", "features": feats}

    anim_days = sorted(features_by_date)
    if not anim_days:
        st.info("No warnings in the recent window.")
        return

    st.subheader("31-day danger map — drag or play to animate")

    @st.fragment
    def _animated_danger_map() -> None:
        anim_key = f"{anim_end}|{len(anim_days)}"
        if st.session_state.get("_home_key") != anim_key:
            st.session_state["_home_key"] = anim_key
            st.session_state["_home_idx"] = len(anim_days) - 1
            st.session_state["_home_play"] = False

        playing = st.session_state["_home_play"]
        c1, c2, c3 = st.columns([1, 1, 3])
        if c1.button("⏸ Pause" if playing else "▶ Play", key="home_play_btn"):
            st.session_state["_home_play"] = not playing
            st.rerun(scope="fragment")
        speed = c2.selectbox(
            "Speed", ["0.3s", "0.6s", "1.0s"], index=1, label_visibility="collapsed", key="home_speed"
        )
        slider_val = c3.slider(
            f"Day  ·  {anim_start} → {anim_end}",
            min_value=0,
            max_value=len(anim_days) - 1,
            value=st.session_state["_home_idx"],
            format="",
            key="home_slider",
        )
        # Slider owns idx only when paused; loop owns it during playback.
        if not playing:
            st.session_state["_home_idx"] = slider_val

        metric_slot = st.empty()
        map_slot = st.empty()

        def _render(idx: int) -> None:
            day = anim_days[idx]
            fc = features_by_date[day]
            counts: dict[int, int] = {}
            for f in fc["features"]:
                lvl = f["properties"]["danger_level"]
                counts[lvl] = counts.get(lvl, 0) + 1

            with metric_slot.container():
                mcols = st.columns(6)
                mcols[0].metric("Date", day.strftime("%Y-%m-%d"))
                for i, lvl in enumerate([1, 2, 3, 4, 5]):
                    mcols[i + 1].metric(f"Level {lvl}", counts.get(lvl, 0))
            map_slot.pydeck_chart(
                pdk.Deck(
                    map_style="light",
                    initial_view_state=pdk.ViewState(latitude=65, longitude=15, zoom=3.5),
                    layers=[
                        pdk.Layer(
                            "GeoJsonLayer",
                            data=fc,
                            get_fill_color="properties.fill_color",
                            get_line_color=[40, 40, 40],
                            line_width_min_pixels=1,
                            pickable=True,
                            stroked=True,
                            filled=True,
                        )
                    ],
                    tooltip={"text": "{region_name}\nDanger level: {danger_level}"},
                )
            )

        if playing:
            delay = {"0.3s": 0.3, "0.6s": 0.6, "1.0s": 1.0}[speed]
            while st.session_state["_home_play"]:
                idx = st.session_state["_home_idx"]
                _render(idx)
                time.sleep(delay)
                st.session_state["_home_idx"] = (idx + 1) % len(anim_days)
        else:
            _render(st.session_state["_home_idx"])

    _animated_danger_map()

    latest_day = anim_days[-1]
    latest = warnings[warnings["date"].apply(lambda d: (d.date() if hasattr(d, "date") else d) == latest_day)]

    st.subheader(f"Danger level heatmap by region (60-day window ending {latest_day})")
    heatmap = query(
        f"""
        select date::date as date, region_name,
               avg(try_cast(danger_level as integer)) as danger_level
        from {AVA}
        where date::date >= ? - interval 60 day
          and date::date <= ?
        group by 1, 2
        order by 1
        """,
        (latest_day, latest_day),
    )
    if not heatmap.empty:
        pivot = heatmap.pivot(index="region_name", columns="date", values="danger_level")
        st.dataframe(
            pivot.style.background_gradient(
                cmap="RdYlGn_r", axis=None, vmin=1, vmax=5
            ).format("{:.1f}", na_rep=""),
            use_container_width=True,
            height=520,
        )

    st.subheader(f"Latest warnings — {latest_day}")
    if not latest.empty:
        st.dataframe(
            latest[["region_name", "danger_level", "main_text"]].sort_values("region_name"),
            use_container_width=True,
            hide_index=True,
        )

    st.caption("Explore: use the sidebar for Region monitor and Weather detail pages.")


if __name__ == "__main__":
    main()
