"""Region monitor — avalanche danger overlaid with weather variables."""

from __future__ import annotations

import datetime as dt
import time

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st

from Home import AVA, REGION_WEATHER_CTE, WX, _bbox_polygon, load_region_geojson, query

st.set_page_config(page_title="Region monitor", layout="wide")


regions = query(f"select distinct region_name from {AVA} order by 1")["region_name"].tolist()
if not regions:
    st.warning("No regions available.")
    st.stop()

with st.sidebar:
    default_idx = regions.index("Lyngen") if "Lyngen" in regions else 0
    region = st.selectbox("Region", regions, index=default_idx)

    dates_df = query(
        f"select min(date::date) as lo, max(date::date) as hi from {AVA} where region_name = ?",
        (region,),
    )
    lo = dates_df.iloc[0]["lo"]
    hi = dates_df.iloc[0]["hi"]
    lo = lo.date() if hasattr(lo, "date") else lo
    hi = hi.date() if hasattr(hi, "date") else hi

    window = st.slider("Days of history", 30, 365, 180, step=30)
    end_date: dt.date = st.date_input("End date", value=hi, min_value=lo, max_value=hi)
    start_date = max(lo, end_date - dt.timedelta(days=window))

st.title(f"{region}")
st.caption(f"{start_date} → {end_date}  ·  {(end_date - start_date).days} days")


joined = query(
    REGION_WEATHER_CTE
    + f"""
    select
        a.date::date as date,
        try_cast(a.danger_level as integer) as danger_level,
        a.main_text,
        rw.max_temp, rw.avg_temp, rw.min_temp,
        rw.max_snowfall, rw.avg_snowfall,
        rw.max_rain, rw.avg_rain,
        rw.max_snow_depth, rw.avg_snow_depth,
        rw.max_windspeed, rw.avg_windspeed,
        rw.avg_humidity
    from {AVA} a
    left join region_weather rw
      on rw.region_name = a.region_name and rw.date = a.date::date
    where a.region_name = ?
      and a.date::date between ? and ?
    order by a.date
    """,
    (region, start_date, end_date),
)

if joined.empty:
    st.info("No overlapping data in this window.")
    st.stop()


recent_lvl = joined.dropna(subset=["danger_level"]).tail(1)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Latest danger", int(recent_lvl["danger_level"].iloc[0]) if not recent_lvl.empty else "—")
c2.metric("Peak danger (window)", int(joined["danger_level"].max()) if joined["danger_level"].notna().any() else "—")
c3.metric("Days at ≥3", int((joined["danger_level"] >= 3).sum()))
c4.metric("Total snowfall (avg mm/day)", f"{joined['avg_snowfall'].mean():.1f}" if joined['avg_snowfall'].notna().any() else "—")
c5.metric("Max wind (m/s)", f"{joined['max_windspeed'].max():.1f}" if joined['max_windspeed'].notna().any() else "—")


st.subheader("Danger level with weather overlay")

WEATHER_VARS: dict[str, tuple[str, str]] = {
    "avg_temp": ("Avg temperature (°C)", "temperature"),
    "max_snowfall": ("Max snowfall (mm)", "snowfall"),
    "max_rain": ("Max rain (mm)", "rain"),
    "avg_snow_depth": ("Avg snow depth (cm)", "snow"),
    "max_windspeed": ("Max wind (m/s)", "wind"),
    "avg_humidity": ("Avg humidity (%)", "humidity"),
}

selected_vars = st.multiselect(
    "Weather variables to overlay",
    options=list(WEATHER_VARS.keys()),
    default=["avg_temp", "max_snowfall", "max_windspeed"],
    format_func=lambda k: WEATHER_VARS[k][0],
)

def _danger_chart(df: pd.DataFrame) -> alt.Chart:
    return (
        alt.Chart(df)
        .mark_bar(size=6)
        .encode(
            x=alt.X("date:T", title=None),
            y=alt.Y("danger_level:Q", title="Danger", scale=alt.Scale(domain=[0, 5])),
            color=alt.Color(
                "danger_level:O",
                scale=alt.Scale(
                    domain=[1, 2, 3, 4, 5],
                    range=["#1a9850", "#ffff33", "#fdae61", "#f46d43", "#7f0000"],
                ),
                legend=alt.Legend(title="Danger"),
            ),
            tooltip=["date:T", "danger_level:Q"],
        )
        .properties(height=140)
    )


st.altair_chart(_danger_chart(joined), use_container_width=True)

for var in selected_vars:
    label, _ = WEATHER_VARS[var]
    sub = joined[["date", var, "danger_level"]].dropna(subset=[var])
    if sub.empty:
        continue
    line = (
        alt.Chart(sub)
        .mark_line(point=False)
        .encode(
            x=alt.X("date:T", title=None),
            y=alt.Y(f"{var}:Q", title=label),
            tooltip=["date:T", alt.Tooltip(f"{var}:Q", format=".2f"), "danger_level:Q"],
        )
    )
    # Shade elevated-danger days so the eye anchors on high-risk periods.
    danger_bg = (
        alt.Chart(sub.dropna(subset=["danger_level"]))
        .transform_filter("datum.danger_level >= 3")
        .mark_rule(strokeWidth=8, opacity=0.15, color="#7f0000")
        .encode(x="date:T")
    )
    st.altair_chart((danger_bg + line).properties(height=180), use_container_width=True)


st.subheader("How each weather variable tracks danger")

corr_df = joined.dropna(subset=["danger_level"]).copy()
if len(corr_df) < 5:
    st.info("Need at least 5 days with a danger level to plot correlations.")
    st.stop()

metric_cols = list(WEATHER_VARS.keys())
labels_map = {c: WEATHER_VARS[c][0] for c in metric_cols}

spearman = (
    corr_df[["danger_level", *metric_cols]]
    .corr(method="spearman")["danger_level"]
    .drop("danger_level")
)
coef_df = pd.DataFrame(
    {"variable": [labels_map[c] for c in metric_cols], "spearman": spearman.values}
).sort_values("spearman", key=lambda s: s.abs(), ascending=False)

bar = (
    alt.Chart(coef_df)
    .mark_bar()
    .encode(
        x=alt.X("spearman:Q", title="Spearman ρ (monotonic association with danger)",
                scale=alt.Scale(domain=[-1, 1])),
        y=alt.Y("variable:N", sort="-x", title=None),
        color=alt.Color(
            "spearman:Q",
            scale=alt.Scale(scheme="redblue", domain=[-1, 1], reverse=True),
            legend=None,
        ),
        tooltip=[alt.Tooltip("variable:N"), alt.Tooltip("spearman:Q", format="+.2f")],
    )
    .properties(height=32 * len(coef_df))
)
zero = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#333").encode(x="x:Q")
st.altair_chart(bar + zero, use_container_width=True)
st.caption(
    "Positive bars → variable rises with danger. Negative → falls. "
    "Longer bar = stronger monotonic association."
)

st.subheader("Distribution by danger level")

long = corr_df[["danger_level", *metric_cols]].melt(
    id_vars="danger_level", var_name="var_key", value_name="value"
).dropna(subset=["value"])
long["variable"] = long["var_key"].map(labels_map)
long["danger_str"] = long["danger_level"].astype(int).astype(str)

danger_scale = alt.Scale(
    domain=["1", "2", "3", "4", "5"],
    range=["#1a9850", "#ffff33", "#fdae61", "#f46d43", "#7f0000"],
)

box = (
    alt.Chart(long)
    .mark_boxplot(extent="min-max")
    .encode(
        x=alt.X("danger_str:N", title="Danger", sort=["1", "2", "3", "4", "5"]),
        y=alt.Y("value:Q", title=None, scale=alt.Scale(zero=False)),
        color=alt.Color("danger_str:N", scale=danger_scale, legend=None),
    )
    .properties(width=220, height=200)
    .facet(facet=alt.Facet("variable:N", title=None), columns=3)
    .resolve_scale(y="independent")
)
st.altair_chart(box, use_container_width=True)

st.subheader("31-day weather map — drag to animate")

anim_var = st.selectbox(
    "Variable",
    options=metric_cols,
    format_func=lambda k: WEATHER_VARS[k][0],
    index=metric_cols.index("max_snowfall") if "max_snowfall" in metric_cols else 0,
    key="anim_var",
)

anim_end = end_date
anim_start = anim_end - dt.timedelta(days=31)

_WX_COL = {
    "avg_temp": "average_temperature",
    "max_snowfall": "max_snowfall",
    "max_rain": "max_rain",
    "avg_snow_depth": "average_snow_depth",
    "max_windspeed": "max_windspeed",
    "avg_humidity": "average_relative_humidity",
}
_wx_col = _WX_COL[anim_var]

cells = query(
    f"""
    select
        date::date as date,
        east_south_lat, east_south_lon, west_north_lat, west_north_lon,
        (east_south_lat + west_north_lat) / 2.0 as clat,
        (east_south_lon + west_north_lon) / 2.0 as clon,
        {_wx_col} as value
    from {WX}
    where date::date between ? and ?
    """,
    (anim_start, anim_end),
)

region_row = query(
    f"""
    select distinct
        least(east_south_lat, west_north_lat) as lat_min,
        greatest(east_south_lat, west_north_lat) as lat_max,
        least(east_south_lon, west_north_lon) as lon_min,
        greatest(east_south_lon, west_north_lon) as lon_max,
        region_id
    from {AVA}
    where region_name = ?
    limit 1
    """,
    (region,),
)

if cells.empty or region_row.empty:
    st.info("No weather cells for this region in the last 31 days.")
else:
    rb = region_row.iloc[0]
    inside_mask = (
        (cells["clat"] >= rb["lat_min"]) & (cells["clat"] <= rb["lat_max"])
        & (cells["clon"] >= rb["lon_min"]) & (cells["clon"] <= rb["lon_max"])
    )
    inside = cells[inside_mask]

    if inside.empty:
        rc_lat = (rb["lat_min"] + rb["lat_max"]) / 2
        rc_lon = (rb["lon_min"] + rb["lon_max"]) / 2
        per_cell = (
            cells.groupby(["clat", "clon"], as_index=False)
            .first()
            .assign(_d=lambda d: ((d["clat"] - rc_lat) ** 2 + (d["clon"] - rc_lon) ** 2))
            .nsmallest(9, "_d")[["clat", "clon"]]
        )
        in_region = cells.merge(per_cell, on=["clat", "clon"], how="inner").copy()
        in_region["in_region"] = False
    else:
        # Grid spacing from unique centres; 1.5x tolerance catches diagonal neighbours
        # without picking up the next ring.
        uniq_lat = sorted(cells["clat"].unique())
        uniq_lon = sorted(cells["clon"].unique())
        dlat = min((b - a for a, b in zip(uniq_lat, uniq_lat[1:])), default=0.1)
        dlon = min((b - a for a, b in zip(uniq_lon, uniq_lon[1:])), default=0.1)
        tol_lat, tol_lon = 1.5 * dlat, 1.5 * dlon

        in_lats = inside["clat"].to_numpy()
        in_lons = inside["clon"].to_numpy()
        clat = cells["clat"].to_numpy()[:, None]
        clon = cells["clon"].to_numpy()[:, None]
        near = ((abs(clat - in_lats) <= tol_lat) & (abs(clon - in_lons) <= tol_lon)).any(axis=1)

        in_region = cells[near].copy()
        in_region["in_region"] = inside_mask[near].to_numpy()

    if in_region.empty:
        st.info("No weather cells fall inside this region's bbox.")
    else:
        in_region["date"] = pd.to_datetime(in_region["date"]).dt.date
        available_days = sorted(in_region["date"].unique())

        outline = None
        try:
            geo = load_region_geojson()
            rid = int(rb["region_id"])
            outline = next(
                (f for f in geo["features"] if int(f["properties"]["omradeID"]) == rid),
                None,
            )
        except Exception:
            outline = None

        center_lat = (rb["lat_min"] + rb["lat_max"]) / 2
        center_lon = (rb["lon_min"] + rb["lon_max"]) / 2
        vmin = float(in_region["value"].min())
        vmax = float(in_region["value"].max())
        span = max(vmax - vmin, 1e-6)
        var_label = WEATHER_VARS[anim_var][0]

        # Precompute polygons + colours once for the whole window so fragment ticks
        # only mask by date instead of running .apply per row per frame.
        in_region = in_region.dropna(subset=["value"]).copy()
        in_region["polygon"] = in_region.apply(_bbox_polygon, axis=1)
        _f = ((in_region["value"] - vmin) / span).clip(0, 1)
        in_region["color"] = [
            [int(255 * f), 64, int(255 * (1 - f)), 200 if inside else 70]
            for f, inside in zip(_f.tolist(), in_region["in_region"].tolist())
        ]

        @st.fragment
        def _animated_region_map() -> None:
            # Reset frame when window/region/variable changes to avoid stale indices.
            anim_key = f"{region}|{anim_end}|{anim_var}|{len(available_days)}"
            if st.session_state.get("_anim_key") != anim_key:
                st.session_state["_anim_key"] = anim_key
                st.session_state["_anim_idx"] = len(available_days) - 1
                st.session_state["_anim_play"] = False

            playing = st.session_state["_anim_play"]
            ctrl1, ctrl2, ctrl3 = st.columns([1, 1, 3])
            if ctrl1.button("⏸ Pause" if playing else "▶ Play"):
                st.session_state["_anim_play"] = not playing
                st.rerun(scope="fragment")
            speed = ctrl2.selectbox("Speed", ["0.3s", "0.6s", "1.0s"], index=1, label_visibility="collapsed")
            slider_val = ctrl3.slider(
                f"Day  ·  {anim_start} → {anim_end}",
                min_value=0,
                max_value=len(available_days) - 1,
                value=st.session_state["_anim_idx"],
                format="",
            )
            # Slider drives idx only when paused; during playback the loop owns it.
            if not playing:
                st.session_state["_anim_idx"] = slider_val

            metric_slot = st.empty()
            map_slot = st.empty()
            st.caption(
                f"Colour scale is fixed across the full 31-day window "
                f"({vmin:.1f} → {vmax:.1f}), so cells stay comparable as you drag. "
                "Black outline = varsom region boundary."
            )

            def _render(idx: int) -> None:
                selected_day = available_days[idx]
                day_cells = in_region[in_region["date"] == selected_day]

                layers = [
                    pdk.Layer(
                        "PolygonLayer",
                        data=day_cells,
                        get_polygon="polygon",
                        get_fill_color="color",
                        get_line_color=[80, 80, 80],
                        line_width_min_pixels=0.5,
                        pickable=True,
                        stroked=True,
                        filled=True,
                        opacity=0.75,
                    )
                ]
                if outline is not None:
                    layers.append(
                        pdk.Layer(
                            "GeoJsonLayer",
                            data={"type": "FeatureCollection", "features": [outline]},
                            get_fill_color=[0, 0, 0, 0],
                            get_line_color=[0, 0, 0],
                            line_width_min_pixels=3,
                            stroked=True,
                            filled=False,
                        )
                    )

                danger_today = joined.loc[
                    pd.to_datetime(joined["date"]).dt.date == selected_day, "danger_level"
                ]
                danger_val = int(danger_today.iloc[0]) if not danger_today.empty and pd.notna(danger_today.iloc[0]) else None

                with metric_slot.container():
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Date", selected_day.strftime("%Y-%m-%d"))
                    m2.metric("Danger level", danger_val if danger_val is not None else "—")
                    m3.metric(
                        f"{var_label} (region avg)",
                        f"{day_cells.loc[day_cells['in_region'], 'value'].mean():.1f}" if day_cells["in_region"].any() else "—",
                    )
                map_slot.pydeck_chart(
                    pdk.Deck(
                        map_style="light",
                        initial_view_state=pdk.ViewState(
                            latitude=center_lat, longitude=center_lon, zoom=6.2
                        ),
                        layers=layers,
                        tooltip={"text": f"{var_label}: {{value}}"},
                    )
                )

            if playing:
                delay = {"0.3s": 0.3, "0.6s": 0.6, "1.0s": 1.0}[speed]
                while st.session_state["_anim_play"]:
                    idx = st.session_state["_anim_idx"]
                    _render(idx)
                    time.sleep(delay)
                    st.session_state["_anim_idx"] = (idx + 1) % len(available_days)
            else:
                _render(st.session_state["_anim_idx"])

        _animated_region_map()


st.subheader("Warnings with weather context")
show_cols = [
    "date", "danger_level",
    "avg_temp", "max_snowfall", "max_rain", "avg_snow_depth", "max_windspeed",
    "main_text",
]
tbl = joined[show_cols].sort_values("date", ascending=False)
st.dataframe(
    tbl,
    use_container_width=True,
    hide_index=True,
    column_config={
        "date": st.column_config.DateColumn("Date"),
        "danger_level": st.column_config.NumberColumn("Danger", format="%d"),
        "avg_temp": st.column_config.NumberColumn("Temp °C", format="%.1f"),
        "max_snowfall": st.column_config.NumberColumn("Snowfall mm", format="%.1f"),
        "max_rain": st.column_config.NumberColumn("Rain mm", format="%.1f"),
        "avg_snow_depth": st.column_config.NumberColumn("Snow depth cm", format="%.0f"),
        "max_windspeed": st.column_config.NumberColumn("Wind m/s", format="%.1f"),
        "main_text": st.column_config.TextColumn("Summary", width="large"),
    },
)
