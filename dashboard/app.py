import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configure page
st.set_page_config(
    page_title="Boreas Weather Dashboard",
    page_icon="🌨️",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_db_connection():
    return duckdb.connect("./boreas.duckdb", read_only=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_weather_data():
    conn = get_db_connection()
    query = """
    SELECT 
        time,
        temperature_2m,
        relative_humidity_2m,
        precipitation,
        windspeed_10m,
        region_id,
        weather_type
    FROM "2_silver".fact_weather
    ORDER BY time DESC
    LIMIT 10000
    """
    return conn.execute(query).df()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_regions_data():
    regions = [
        {"region_id": "3003", "name": "Nordenskiöld Land", "lat": 77.9, "lon": 15.75},
        {"region_id": "3006", "name": "Finnmarkskysten", "lat": 70.8, "lon": 27.0},
        {"region_id": "3007", "name": "Vest-Finnmark", "lat": 69.9, "lon": 22.0},
        {"region_id": "3009", "name": "Nord-Troms", "lat": 70.3, "lon": 21.25},
        {"region_id": "3010", "name": "Lyngen", "lat": 69.65, "lon": 20.25},
        {"region_id": "3011", "name": "Tromsø", "lat": 69.5, "lon": 19.0},
        {"region_id": "3012", "name": "Sør-Troms", "lat": 69.1, "lon": 19.0},
        {"region_id": "3013", "name": "Indre Troms", "lat": 68.85, "lon": 20.0},
        {"region_id": "3014", "name": "Lofoten og Vesterålen", "lat": 68.35, "lon": 13.75},
        {"region_id": "3015", "name": "Ofoten", "lat": 68.2, "lon": 17.0},
        {"region_id": "3016", "name": "Salten", "lat": 67.3, "lon": 15.0},
        {"region_id": "3017", "name": "Svartisen", "lat": 66.6, "lon": 14.25},
        {"region_id": "3018", "name": "Helgeland", "lat": 65.85, "lon": 13.5},
        {"region_id": "3022", "name": "Trollheimen", "lat": 62.78, "lon": 9.19},
        {"region_id": "3023", "name": "Romsdal", "lat": 62.4, "lon": 7.5},
        {"region_id": "3024", "name": "Sunnmøre", "lat": 62.1, "lon": 6.75},
        {"region_id": "3026", "name": "Indre Fjordane", "lat": 61.3, "lon": 6.75},
        {"region_id": "3028", "name": "Jotunheimen", "lat": 61.5, "lon": 8.25},
        {"region_id": "3029", "name": "Indre Sogn", "lat": 61.0, "lon": 7.5},
        {"region_id": "3031", "name": "Voss", "lat": 60.5, "lon": 6.75},
        {"region_id": "3032", "name": "Hallingdal", "lat": 60.6, "lon": 8.75},
        {"region_id": "3034", "name": "Hardanger", "lat": 60.3, "lon": 7.0},
        {"region_id": "3035", "name": "Vest-Telemark", "lat": 59.4, "lon": 8.0},
        {"region_id": "3037", "name": "Heiane", "lat": 59.55, "lon": 5.75}
    ]
    return pd.DataFrame(regions)

def main():
    st.title("🌨️ Boreas Weather Dashboard")
    st.markdown("Real-time weather data from Norwegian avalanche regions")
    
    # Load data
    try:
        weather_df = load_weather_data()
        regions_df = load_regions_data()
        
        # Merge weather data with region coordinates
        merged_df = weather_df.merge(regions_df, on='region_id', how='left')
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Region filter
        available_regions = sorted(merged_df['name'].dropna().unique())
        selected_regions = st.sidebar.multiselect(
            "Select Regions", 
            available_regions, 
            default=available_regions[:5]
        )
        
        # Weather type filter
        weather_types = merged_df['weather_type'].unique()
        selected_weather_type = st.sidebar.selectbox(
            "Weather Type",
            options=weather_types,
            index=0
        )
        
        # Date range filter
        if not merged_df.empty:
            min_date = merged_df['time'].min().date()
            max_date = merged_df['time'].max().date()
            
            selected_date_range = st.sidebar.date_input(
                "Date Range",
                value=(max_date - timedelta(days=7), max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        # Filter data
        filtered_df = merged_df[
            (merged_df['name'].isin(selected_regions)) &
            (merged_df['weather_type'] == selected_weather_type)
        ]
        
        if len(selected_date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['time'].dt.date >= selected_date_range[0]) &
                (filtered_df['time'].dt.date <= selected_date_range[1])
            ]
        
        # Main dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        if not filtered_df.empty:
            with col1:
                avg_temp = filtered_df['temperature_2m'].mean()
                st.metric("Avg Temperature", f"{avg_temp:.1f}°C")
            
            with col2:
                avg_humidity = filtered_df['relative_humidity_2m'].mean()
                st.metric("Avg Humidity", f"{avg_humidity:.1f}%")
            
            with col3:
                total_precip = filtered_df['precipitation'].sum()
                st.metric("Total Precipitation", f"{total_precip:.1f}mm")
            
            with col4:
                avg_wind = filtered_df['windspeed_10m'].mean()
                st.metric("Avg Wind Speed", f"{avg_wind:.1f} m/s")
        
        # Map visualization
        st.subheader("Weather Map")
        
        if not filtered_df.empty and 'lat' in filtered_df.columns:
            # Get latest data for each region
            latest_data = filtered_df.groupby('region_id').last().reset_index()
            
            # Create map
            fig_map = px.scatter_mapbox(
                latest_data,
                lat="lat",
                lon="lon",
                color="temperature_2m",
                size="windspeed_10m",
                hover_name="name",
                hover_data={
                    "temperature_2m": ":.1f",
                    "relative_humidity_2m": ":.1f",
                    "precipitation": ":.1f",
                    "windspeed_10m": ":.1f"
                },
                color_continuous_scale="RdYlBu_r",
                mapbox_style="open-street-map",
                zoom=4,
                center={"lat": 65, "lon": 15},
                height=600,
                title="Current Weather Conditions"
            )
            
            fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        
        # Time series charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Temperature Trends")
            if not filtered_df.empty:
                fig_temp = px.line(
                    filtered_df,
                    x="time",
                    y="temperature_2m",
                    color="name",
                    title="Temperature Over Time"
                )
                fig_temp.update_layout(height=400)
                st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            st.subheader("Precipitation")
            if not filtered_df.empty:
                fig_precip = px.bar(
                    filtered_df.groupby(['name', 'time'])['precipitation'].sum().reset_index(),
                    x="time",
                    y="precipitation",
                    color="name",
                    title="Precipitation Over Time"
                )
                fig_precip.update_layout(height=400)
                st.plotly_chart(fig_precip, use_container_width=True)
        
        # Data table
        st.subheader("Raw Data")
        if not filtered_df.empty:
            st.dataframe(
                filtered_df[['time', 'name', 'temperature_2m', 'relative_humidity_2m', 
                           'precipitation', 'windspeed_10m', 'weather_type']].head(100),
                use_container_width=True
            )
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure the duckdb database exists at './boreas.duckdb' and contains the fact_weather table")

if __name__ == "__main__":
    main()