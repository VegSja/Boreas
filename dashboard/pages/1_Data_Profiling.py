import os
import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Data Profiling – Boreas",
    page_icon="🔍",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------
DB_PATH = os.environ.get("BOREAS_DB_PATH", "./boreas.duckdb")


@st.cache_resource
def get_db_connection():
    return duckdb.connect(DB_PATH, read_only=True)


@st.cache_data(ttl=300)
def load_avalanche_data() -> pd.DataFrame:
    conn = get_db_connection()
    return conn.execute(
        """
        SELECT
            date,
            region_id,
            region_name,
            danger_level,
            valid_from,
            valid_to,
            main_text
        FROM "3_gold"."avalanche_per_region"
        WHERE date IS NOT NULL
        ORDER BY date DESC, region_name
        """
    ).df()


@st.cache_data(ttl=300)
def load_weather_data() -> pd.DataFrame:
    conn = get_db_connection()
    return conn.execute(
        """
        SELECT
            date,
            max_temp,
            average_temperature,
            min_temp,
            max_relative_humidity,
            average_relative_humidity,
            min_relative_humidity,
            max_snowfall,
            average_snowfall,
            max_rain,
            average_rain,
            max_snow_depth,
            average_snow_depth,
            max_windspeed,
            average_windspeed,
            min_windspeed,
            weather_type
        FROM "3_gold"."weather_per_region"
        WHERE date IS NOT NULL
        ORDER BY date DESC
        """
    ).df()


# ---------------------------------------------------------------------------
# Profiling helpers
# ---------------------------------------------------------------------------

def missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame summarising missing values per column."""
    total = len(df)
    missing = df.isnull().sum()
    pct = (missing / total * 100).round(2)
    return (
        pd.DataFrame({"Missing Count": missing, "Missing (%)": pct})
        .query("`Missing Count` > 0")
        .sort_values("Missing (%)", ascending=False)
    )


def detect_outliers_iqr(series: pd.Series) -> pd.Series:
    """Return a boolean mask of IQR-based outliers."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (series < lower) | (series > upper)


def outlier_summary(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    """Return a DataFrame with outlier statistics for each numeric column."""
    rows = []
    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        mask = detect_outliers_iqr(series)
        count = int(mask.sum())
        pct = round(count / len(series) * 100, 2)
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        rows.append(
            {
                "Column": col,
                "Outlier Count": count,
                "Outlier (%)": pct,
                "IQR Lower Bound": round(q1 - 1.5 * iqr, 3),
                "IQR Upper Bound": round(q3 + 1.5 * iqr, 3),
                "Min": round(series.min(), 3),
                "Max": round(series.max(), 3),
            }
        )
    return pd.DataFrame(rows).sort_values("Outlier (%)", ascending=False)


def descriptive_stats(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    """Return descriptive statistics for numeric columns."""
    return df[numeric_cols].describe().T.round(3)


# ---------------------------------------------------------------------------
# Page content
# ---------------------------------------------------------------------------

def render_alerts(
    avalanche_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    weather_numeric_cols: list[str],
) -> None:
    """Render an alert banner for significant anomalies."""
    alerts: list[str] = []

    # --- Missing value alerts ---
    if not avalanche_df.empty:
        mv = missing_value_summary(avalanche_df)
        critical = mv[mv["Missing (%)"] > 20]
        for col, row in critical.iterrows():
            alerts.append(
                f"⚠️ **Avalanche** – column `{col}` has **{row['Missing (%)']:.1f}%** missing values."
            )

    if not weather_df.empty:
        mv = missing_value_summary(weather_df)
        critical = mv[mv["Missing (%)"] > 20]
        for col, row in critical.iterrows():
            alerts.append(
                f"⚠️ **Weather** – column `{col}` has **{row['Missing (%)']:.1f}%** missing values."
            )

    # --- Outlier alerts ---
    if not weather_df.empty and weather_numeric_cols:
        outliers = outlier_summary(weather_df, weather_numeric_cols)
        flagged = outliers[outliers["Outlier (%)"] > 5]
        for _, row in flagged.iterrows():
            alerts.append(
                f"🔴 **Weather outliers** – `{row['Column']}` has **{row['Outlier (%)']:.1f}%** "
                f"outliers (expected range: {row['IQR Lower Bound']} – {row['IQR Upper Bound']})."
            )

    # --- Danger level range alert ---
    if not avalanche_df.empty and "danger_level" in avalanche_df.columns:
        danger_numeric = pd.to_numeric(avalanche_df["danger_level"], errors="coerce").dropna()
        if not danger_numeric.empty:
            invalid = danger_numeric[(danger_numeric < 1) | (danger_numeric > 5)]
            if not invalid.empty:
                alerts.append(
                    f"🔴 **Avalanche** – {len(invalid)} record(s) with `danger_level` outside "
                    f"the valid range 1–5 detected."
                )

    if alerts:
        with st.container():
            st.subheader("🚨 Data Quality Alerts")
            for alert in alerts:
                st.warning(alert)
    else:
        st.success("✅ No significant data quality issues detected.")


def render_overview(avalanche_df: pd.DataFrame, weather_df: pd.DataFrame) -> None:
    """Render dataset overview cards and missing-value charts."""
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Avalanche Dataset")
        if avalanche_df.empty:
            st.info("No avalanche data available.")
        else:
            a_date_min = avalanche_df["date"].min()
            a_date_max = avalanche_df["date"].max()
            st.metric("Total Records", f"{len(avalanche_df):,}")
            st.metric("Unique Regions", avalanche_df["region_name"].nunique())
            st.metric("Date Range", f"{a_date_min} → {a_date_max}")

            mv = missing_value_summary(avalanche_df)
            if mv.empty:
                st.success("No missing values in avalanche data.")
            else:
                fig = px.bar(
                    mv.reset_index(),
                    x="index",
                    y="Missing (%)",
                    title="Avalanche – Missing Values (%)",
                    labels={"index": "Column"},
                    color="Missing (%)",
                    color_continuous_scale="Reds",
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Weather Dataset")
        if weather_df.empty:
            st.info("No weather data available.")
        else:
            w_date_min = weather_df["date"].min()
            w_date_max = weather_df["date"].max()
            st.metric("Total Records", f"{len(weather_df):,}")
            st.metric("Date Range", f"{w_date_min} → {w_date_max}")

            mv = missing_value_summary(weather_df)
            if mv.empty:
                st.success("No missing values in weather data.")
            else:
                fig = px.bar(
                    mv.reset_index(),
                    x="index",
                    y="Missing (%)",
                    title="Weather – Missing Values (%)",
                    labels={"index": "Column"},
                    color="Missing (%)",
                    color_continuous_scale="Reds",
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)


def render_distributions(
    avalanche_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    weather_numeric_cols: list[str],
) -> None:
    """Render distribution histograms and box plots."""
    st.subheader("Avalanche – Danger Level Distribution")
    if not avalanche_df.empty and "danger_level" in avalanche_df.columns:
        danger_df = avalanche_df.copy()
        danger_df["danger_level"] = pd.to_numeric(
            danger_df["danger_level"], errors="coerce"
        )
        danger_df = danger_df.dropna(subset=["danger_level"])

        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                danger_df,
                x="danger_level",
                nbins=5,
                title="Danger Level Frequency",
                color_discrete_sequence=["#e85b4a"],
                labels={"danger_level": "Danger Level"},
            )
            fig.update_layout(height=320)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            region_avg = (
                danger_df.groupby("region_name")["danger_level"]
                .mean()
                .reset_index()
                .sort_values("danger_level", ascending=False)
            )
            fig = px.bar(
                region_avg,
                x="danger_level",
                y="region_name",
                orientation="h",
                title="Average Danger Level by Region",
                color="danger_level",
                color_continuous_scale="RdYlGn_r",
                labels={"danger_level": "Avg Danger Level", "region_name": "Region"},
            )
            fig.update_layout(height=420, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No avalanche data available for distribution analysis.")

    st.divider()
    st.subheader("Weather – Numeric Column Distributions")

    if weather_df.empty or not weather_numeric_cols:
        st.info("No weather data available for distribution analysis.")
        return

    selected_col = st.selectbox(
        "Select weather variable to inspect",
        options=weather_numeric_cols,
        format_func=lambda c: c.replace("_", " ").title(),
        key="dist_col",
    )

    series = weather_df[selected_col].dropna()
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            series.to_frame(),
            x=selected_col,
            nbins=40,
            title=f"Histogram – {selected_col.replace('_', ' ').title()}",
            color_discrete_sequence=["#1f77b4"],
        )
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        outlier_mask = detect_outliers_iqr(series)
        plot_df = series.to_frame()
        plot_df["outlier"] = outlier_mask
        fig = px.box(
            plot_df,
            y=selected_col,
            title=f"Box Plot – {selected_col.replace('_', ' ').title()}",
            color_discrete_sequence=["#1f77b4"],
        )
        # Overlay outlier points
        outlier_points = plot_df[plot_df["outlier"]]
        if not outlier_points.empty:
            fig.add_trace(
                go.Scatter(
                    y=outlier_points[selected_col],
                    mode="markers",
                    marker=dict(color="red", size=7, symbol="x"),
                    name="Outlier",
                )
            )
        fig.update_layout(height=340)
        st.plotly_chart(fig, use_container_width=True)


def render_outliers(
    weather_df: pd.DataFrame,
    avalanche_df: pd.DataFrame,
    weather_numeric_cols: list[str],
) -> None:
    """Render outlier summary tables and time-series highlighting."""
    st.subheader("Weather – Outlier Summary (IQR Method)")
    if not weather_df.empty and weather_numeric_cols:
        outliers = outlier_summary(weather_df, weather_numeric_cols)
        st.dataframe(
            outliers.style.background_gradient(subset=["Outlier (%)"], cmap="Reds"),
            use_container_width=True,
        )

        st.subheader("Outliers over Time")
        selected_col = st.selectbox(
            "Select weather variable for time-series outlier view",
            options=weather_numeric_cols,
            format_func=lambda c: c.replace("_", " ").title(),
            key="outlier_ts_col",
        )
        if "date" in weather_df.columns:
            ts_df = weather_df[["date", selected_col]].dropna().copy()
            ts_df["outlier"] = detect_outliers_iqr(ts_df[selected_col])
            normal = ts_df[~ts_df["outlier"]]
            anomaly = ts_df[ts_df["outlier"]]

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=normal["date"],
                    y=normal[selected_col],
                    mode="lines+markers",
                    name="Normal",
                    marker=dict(color="#1f77b4", size=4),
                    line=dict(color="#1f77b4"),
                )
            )
            if not anomaly.empty:
                fig.add_trace(
                    go.Scatter(
                        x=anomaly["date"],
                        y=anomaly[selected_col],
                        mode="markers",
                        name="Outlier",
                        marker=dict(color="red", size=9, symbol="x"),
                    )
                )
            fig.update_layout(
                title=f"Time-series – {selected_col.replace('_', ' ').title()} with Outliers",
                xaxis_title="Date",
                yaxis_title=selected_col.replace("_", " ").title(),
                height=380,
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No weather data available for outlier analysis.")

    st.divider()
    st.subheader("Avalanche – Danger Level Anomalies")
    if not avalanche_df.empty and "danger_level" in avalanche_df.columns:
        danger_series = pd.to_numeric(
            avalanche_df["danger_level"], errors="coerce"
        ).dropna()
        invalid = danger_series[(danger_series < 1) | (danger_series > 5)]
        if invalid.empty:
            st.success("All danger level values are within the valid range (1–5).")
        else:
            st.warning(
                f"Found {len(invalid)} record(s) with danger_level outside 1–5."
            )
            st.dataframe(
                avalanche_df.loc[invalid.index, ["date", "region_name", "danger_level"]],
                use_container_width=True,
            )
    else:
        st.info("No avalanche data available for anomaly analysis.")


def render_correlations(
    weather_df: pd.DataFrame, weather_numeric_cols: list[str]
) -> None:
    """Render a correlation heatmap for weather variables."""
    st.subheader("Weather – Correlation Matrix")
    if weather_df.empty or len(weather_numeric_cols) < 2:
        st.info("Not enough weather data to compute correlations.")
        return

    corr = weather_df[weather_numeric_cols].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Pearson Correlation – Weather Variables",
        aspect="auto",
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Descriptive Statistics – Weather Variables")
    stats = descriptive_stats(weather_df, weather_numeric_cols)
    st.dataframe(stats, use_container_width=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.title("🔍 Boreas – Data Profiling")
    st.markdown(
        "Quality and distribution analysis for avalanche danger and weather data. "
        "Outliers are detected using the **IQR method** (values beyond Q1 − 1.5·IQR "
        "or Q3 + 1.5·IQR are flagged)."
    )

    try:
        avalanche_df = load_avalanche_data()
        weather_df = load_weather_data()
    except Exception as exc:
        st.error(f"Could not load data: {exc}")
        st.info(
            "Make sure `boreas.duckdb` exists and the dbt models have been run. "
            f"Current DB path: `{DB_PATH}`"
        )
        return

    # Normalise date columns – work on copies to avoid mutating cached data
    if not avalanche_df.empty and "date" in avalanche_df.columns:
        if avalanche_df["date"].dtype.name.startswith("datetime"):
            avalanche_df = avalanche_df.copy()
            avalanche_df["date"] = avalanche_df["date"].dt.date
    if not weather_df.empty and "date" in weather_df.columns:
        if weather_df["date"].dtype.name.startswith("datetime"):
            weather_df = weather_df.copy()
            weather_df["date"] = weather_df["date"].dt.date

    # Numeric columns for weather
    weather_numeric_cols = [
        c
        for c in [
            "max_temp",
            "average_temperature",
            "min_temp",
            "max_relative_humidity",
            "average_relative_humidity",
            "min_relative_humidity",
            "max_snowfall",
            "average_snowfall",
            "max_rain",
            "average_rain",
            "max_snow_depth",
            "average_snow_depth",
            "max_windspeed",
            "average_windspeed",
            "min_windspeed",
        ]
        if c in weather_df.columns
    ]

    # --- Alert banner (always visible) ---
    render_alerts(avalanche_df, weather_df, weather_numeric_cols)

    st.divider()

    # --- Tabs ---
    tab_overview, tab_dist, tab_outliers, tab_corr = st.tabs(
        ["📋 Overview", "📊 Distributions", "⚠️ Outliers & Anomalies", "🔗 Correlations"]
    )

    with tab_overview:
        render_overview(avalanche_df, weather_df)

    with tab_dist:
        render_distributions(avalanche_df, weather_df, weather_numeric_cols)

    with tab_outliers:
        render_outliers(weather_df, avalanche_df, weather_numeric_cols)

    with tab_corr:
        render_correlations(weather_df, weather_numeric_cols)


if __name__ == "__main__":
    main()
