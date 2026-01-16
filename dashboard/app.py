import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta, date

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
def load_avalanche_data():
    conn = get_db_connection()
    query = """
    SELECT 
        date,
        registration_id,
        region_id,
        region_name,
        danger_level,
        valid_from,
        valid_to,
        main_text,
        east_south_lon,
        east_south_lat,
        west_north_lon,
        west_north_lat
    FROM "3_gold"."avalanche_per_region"
    WHERE date IS NOT NULL
    ORDER BY date DESC, region_name
    """
    return conn.execute(query).df()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_weather_data():
    conn = get_db_connection()
    query = """
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
        min_snowfall,
        max_rain,
        average_rain,
        min_rain,
        max_snow_depth,
        average_snow_depth,
        min_snow_depth,
        max_windspeed,
        average_windspeed,
        min_windspeed,
        weather_type,
        east_south_lon,
        east_south_lat,
        west_north_lon,
        west_north_lat
    FROM "3_gold"."weather_per_region"
    WHERE date IS NOT NULL
    ORDER BY date DESC
    """
    return conn.execute(query).df()

def create_avalanche_map(avalanche_data, selected_date):
    """Create avalanche danger map"""
    # Filter data for the map by selected date
    map_filtered_df = avalanche_data[avalanche_data['date'] == selected_date]
    
    # Get latest data for each region from the selected date
    latest_data = map_filtered_df.groupby('region_id').last().reset_index()
    
    if latest_data.empty:
        return None
        
    # Create map with region boundary squares
    fig_map = go.Figure()
    
    # Add region squares colored by danger level  
    danger_colors = {1: 'rgba(0,128,0,0.4)', 2: 'rgba(255,255,0,0.4)', 
                     3: 'rgba(255,165,0,0.4)', 4: 'rgba(255,0,0,0.4)', 
                     5: 'rgba(139,0,0,0.4)'}    
    for _, row in latest_data.iterrows():
        if pd.notna(row['east_south_lon']) and pd.notna(row['west_north_lon']) and pd.notna(row['danger_level']):
            # Define square corners based on lat/lon bounds
            lons = [row['west_north_lon'], row['east_south_lon'], 
                   row['east_south_lon'], row['west_north_lon'], row['west_north_lon']]
            lats = [row['west_north_lat'], row['west_north_lat'], 
                   row['east_south_lat'], row['east_south_lat'], row['west_north_lat']]
            
            try:
                danger_level = int(float(row['danger_level']))
                color = danger_colors.get(danger_level, 'gray')
            except:
                color = 'gray'
                danger_level = 'N/A'
            
            fig_map.add_trace(go.Scattermapbox(
                lat=lats,
                lon=lons,
                mode='lines',
                fill='toself',
                fillcolor=color,
                line=dict(color='rgba(0,0,0,0)', width=0),
                opacity=0.7,
                hoverinfo='skip',
                showlegend=False
            ))
            
            # Add center point for hover
            center_lat = (row['east_south_lat'] + row['west_north_lat']) / 2
            center_lon = (row['west_north_lon'] + row['east_south_lon']) / 2
            
            fig_map.add_trace(go.Scattermapbox(
                lat=[center_lat],
                lon=[center_lon],
                mode='markers',
                marker=dict(size=20, opacity=0),
                hovertemplate=f'<b>{row["region_name"]}</b><br>' +
                            f'Danger Level: {danger_level}<br>' +
                            '<extra></extra>',
                name=f'{row["region_name"]} (Level {danger_level})',
                showlegend=False
            ))
    
    fig_map.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=65, lon=15),
            zoom=3
        ),
        height=400,
        margin={"r":0,"t":0,"l":0,"b":0},
        title="Avalanche Danger Levels"
    )
    
    return fig_map

def create_weather_map(weather_data, selected_date, weather_variable):
    """Create optimized weather variable map"""
    # Filter data for the map by selected date
    map_filtered_df = weather_data[weather_data['date'] == selected_date]
    
    if map_filtered_df.empty:
        return None
    
    # Create map
    fig_map = go.Figure()
    
    # Define color scales for different variables
    color_scales = {
        'max_temp': 'RdYlBu_r',
        'min_temp': 'RdYlBu_r', 
        'max_precipitation': 'Blues',
        'max_windspeed': 'Viridis',
        'max_relative_humidity': 'BuGn'
    }
    
    color_scale = color_scales.get(weather_variable, 'Viridis')
    
    # Get variable values and create color mapping
    values = map_filtered_df[weather_variable].dropna()
    if values.empty:
        return None
        
    # Normalize values for color mapping
    min_val, max_val = values.min(), values.max()
    if min_val == max_val:
        # If all values are the same, use a single color
        single_color = 'rgba(100,149,237,0.4)'
        for _, row in map_filtered_df.iterrows():
            if pd.notna(row['east_south_lon']) and pd.notna(row['west_north_lon']) and pd.notna(row[weather_variable]):
                # Define square corners based on lat/lon bounds
                lons = [row['west_north_lon'], row['east_south_lon'], 
                       row['east_south_lon'], row['west_north_lon'], row['west_north_lon']]
                lats = [row['west_north_lat'], row['west_north_lat'], 
                       row['east_south_lat'], row['east_south_lat'], row['west_north_lat']]
                
                fig_map.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode='lines',
                    fill='toself',
                    fillcolor=single_color,
                    line=dict(color='rgba(0,0,0,0)', width=0),
                    opacity=0.6,
                    hovertemplate=f'{weather_variable}: {row[weather_variable]:.1f}<br><extra></extra>',
                    showlegend=False
                ))
    else:
        # Use discrete color mapping for better performance
        # Create 5 color bins
        import numpy as np
        bins = np.linspace(min_val, max_val, 6)
        colors = ['rgba(0,0,255,0.4)', 'rgba(0,255,255,0.4)', 'rgba(0,255,0,0.4)', 
                 'rgba(255,255,0,0.4)', 'rgba(255,0,0,0.4)']
        
        for _, row in map_filtered_df.iterrows():
            if pd.notna(row['east_south_lon']) and pd.notna(row['west_north_lon']) and pd.notna(row[weather_variable]):
                # Find color bin
                value = row[weather_variable]
                color_idx = min(4, int((value - min_val) / (max_val - min_val) * 5))
                color = colors[color_idx]
                
                # Define square corners based on lat/lon bounds
                lons = [row['west_north_lon'], row['east_south_lon'], 
                       row['east_south_lon'], row['west_north_lon'], row['west_north_lon']]
                lats = [row['west_north_lat'], row['west_north_lat'], 
                       row['east_south_lat'], row['east_south_lat'], row['west_north_lat']]
                
                fig_map.add_trace(go.Scattermapbox(
                    lat=lats,
                    lon=lons,
                    mode='lines',
                    fill='toself',
                    fillcolor=color,
                    line=dict(color='rgba(0,0,0,0)', width=0),
                    opacity=0.6,
                    hovertemplate=f'{weather_variable}: {value:.1f}<br><extra></extra>',
                    showlegend=False
                ))
    
    fig_map.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=65, lon=15),
            zoom=3
        ),
        height=400,
        margin={"r":0,"t":0,"l":0,"b":0},
        title=f"Weather: {weather_variable.replace('_', ' ').title()}"
    )
    
    return fig_map

def main():
    st.title("🌨️ Boreas Avalanche & Weather Dashboard")
    st.markdown("Integrated avalanche danger and weather data from Norwegian regions")
    
    # Load data
    try:
        avalanche_df = load_avalanche_data()
        weather_df = load_weather_data()
        
        if avalanche_df.empty and weather_df.empty:
            st.warning("No data available. Make sure the dbt models have been run.")
            return
        
        # Clean avalanche data
        if not avalanche_df.empty:
            try:
                # Convert date column to date type if it's datetime
                if avalanche_df['date'].dtype.name.startswith('datetime'):
                    avalanche_df['date'] = avalanche_df['date'].dt.date
                
                # Convert danger_level to numeric, handling any string issues
                if avalanche_df['danger_level'].dtype == 'object':
                    # For string columns, first check for problematic values
                    problematic_mask = avalanche_df['danger_level'].astype(str).str.len() > 2
                    if problematic_mask.any():
                        st.warning(f"Found {problematic_mask.sum()} records with long danger_level values. Removing them.")
                        avalanche_df = avalanche_df[~problematic_mask]
                    
                    avalanche_df['danger_level'] = pd.to_numeric(avalanche_df['danger_level'], errors='coerce')
                
                # Remove rows with invalid danger levels
                avalanche_df = avalanche_df.dropna(subset=['danger_level'])
                    
            except Exception as e:
                st.error(f"Error during avalanche data cleaning: {str(e)}")
                avalanche_df = pd.DataFrame()
        
        # Clean weather data
        if not weather_df.empty:
            try:
                # Convert date column to date type if it's datetime
                if weather_df['date'].dtype.name.startswith('datetime'):
                    weather_df['date'] = weather_df['date'].dt.date
                    
            except Exception as e:
                st.error(f"Error during weather data cleaning: {str(e)}")
                weather_df = pd.DataFrame()
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Region filter (only for avalanche data)
        if not avalanche_df.empty:
            available_regions = sorted(avalanche_df['region_name'].dropna().unique())
            selected_regions = st.sidebar.multiselect(
                "Select Regions (Avalanche)", 
                available_regions, 
                default=available_regions
            )
            
            # Danger level filter
            danger_levels = sorted([int(x) for x in avalanche_df['danger_level'].dropna().unique()])
            selected_danger_levels = st.sidebar.multiselect(
                "Danger Levels",
                danger_levels,
                default=danger_levels
            )
            
            # Filter avalanche data
            filtered_avalanche_df = avalanche_df[
                (avalanche_df['region_name'].isin(selected_regions)) &
                (avalanche_df['danger_level'].isin(selected_danger_levels))
            ]
        else:
            filtered_avalanche_df = pd.DataFrame()
        
        # Weather variable selector (moved from sidebar since it's now above the map)
        # Remove the weather variable selector from sidebar section since it's now above the map
        
        # Date and variable selection for maps
        st.subheader("Maps")
        
        # Get date ranges from both datasets
        available_dates = set()
        if not filtered_avalanche_df.empty:
            available_dates.update(filtered_avalanche_df['date'].dropna())
        if not weather_df.empty:
            available_dates.update(weather_df['date'].dropna())
        
        if available_dates:
            min_date = min(available_dates)
            max_date = max(available_dates)
            
            # Side by side controls
            control_col1, control_col2 = st.columns(2)
            
            with control_col1:
                # Default to today's date, but constrain to available data range
                today = date.today()
                default_date = today if min_date <= today <= max_date else max_date
                
                selected_map_date = st.date_input(
                    "Select Date for Maps",
                    value=default_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="map_date"
                )
            
            with control_col2:
                if not weather_df.empty:
                    # Weather variable selector
                    weather_variables = {
                        'max_temp': 'Max Temperature (°C)',
                        'average_temperature': 'Average Temperature (°C)',
                        'min_temp': 'Min Temperature (°C)',
                        'max_relative_humidity': 'Max Humidity (%)',
                        'average_relative_humidity': 'Average Humidity (%)',
                        'min_relative_humidity': 'Min Humidity (%)',
                        'max_snowfall': 'Max Snowfall (mm)',
                        'average_snowfall': 'Average Snowfall (mm)',
                        'min_snowfall': 'Min Snowfall (mm)',
                        'max_rain': 'Max Rain (mm)',
                        'average_rain': 'Average Rain (mm)',
                        'min_rain': 'Min Rain (mm)',
                        'max_snow_depth': 'Max Snow Depth (cm)',
                        'average_snow_depth': 'Average Snow Depth (cm)',
                        'min_snow_depth': 'Min Snow Depth (cm)',
                        'max_windspeed': 'Max Wind Speed (m/s)',
                        'average_windspeed': 'Average Wind Speed (m/s)',
                        'min_windspeed': 'Min Wind Speed (m/s)'
                    }
                    selected_weather_var = st.selectbox(
                        "Weather Variable", 
                        options=list(weather_variables.keys()),
                        format_func=lambda x: weather_variables[x],
                        index=0,
                        key="weather_var_map"
                    )
            
            # Create side-by-side maps
            map_col1, map_col2 = st.columns(2)
            
            with map_col1:
                if not filtered_avalanche_df.empty:
                    avalanche_map = create_avalanche_map(filtered_avalanche_df, selected_map_date)
                    if avalanche_map:
                        st.plotly_chart(avalanche_map, use_container_width=True)
                    else:
                        st.info("No avalanche data for selected date")
                else:
                    st.info("No avalanche data available")
            
            with map_col2:
                if not weather_df.empty:
                    weather_map = create_weather_map(weather_df, selected_map_date, selected_weather_var)
                    if weather_map:
                        st.plotly_chart(weather_map, use_container_width=True)
                    else:
                        st.info("No weather data for selected date")
                else:
                    st.info("No weather data available")
        
        # Heatmap of danger levels by region (only if avalanche data exists)
        if not filtered_avalanche_df.empty:
            st.subheader("Danger Level Heatmap by Region")
            
            # Date range filter for heatmap
            col1, col2 = st.columns([1, 3])
            with col1:
                min_date = filtered_avalanche_df['date'].min()
                max_date = filtered_avalanche_df['date'].max()
                
                # Default end date to today, start date 30 days before
                today = date.today()
                default_end_date = today if min_date <= today <= max_date else max_date
                default_start_date = min_date
                
                selected_heatmap_range = st.date_input(
                    "Select Date Range for Heatmap",
                    value=(default_start_date, default_end_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="heatmap_date_range"
                )
            
            # Filter data for heatmap by selected date range
            if len(selected_heatmap_range) == 2:
                start_date, end_date = selected_heatmap_range
                heatmap_filtered_df = filtered_avalanche_df[
                    (filtered_avalanche_df['date'] >= start_date) &
                    (filtered_avalanche_df['date'] <= end_date)
                ]
            else:
                heatmap_filtered_df = filtered_avalanche_df
            
            # Create heatmap
            if not heatmap_filtered_df.empty:
                heatmap_df = heatmap_filtered_df.copy()
                heatmap_df['date_str'] = heatmap_df['date'].astype(str)
                
                heatmap_data = heatmap_df.pivot_table(
                    values='danger_level',
                    index='region_name',
                    columns='date_str',
                    aggfunc='mean'
                )
                
                if not heatmap_data.empty:
                    fig_heatmap = px.imshow(
                        heatmap_data,
                        color_continuous_scale='RdYlGn_r',
                        aspect='auto',
                        title="Avalanche Danger Levels by Region Over Time",
                        labels=dict(x="Date", y="Region", color="Danger Level")
                    )
                    fig_heatmap.update_layout(height=500)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Data summary tables
        st.subheader("Recent Data Summary")
        
        # Two column layout for data tables
        table_col1, table_col2 = st.columns(2)
        
        with table_col1:
            if not filtered_avalanche_df.empty:
                st.write("**Avalanche Data**")
                avalanche_summary_cols = ['date', 'region_name', 'danger_level', 'main_text']
                display_avalanche_df = filtered_avalanche_df[avalanche_summary_cols].head(20).copy()
                st.dataframe(display_avalanche_df, use_container_width=True)
        
        with table_col2:
            if not weather_df.empty:
                st.write("**Weather Data**")
                weather_summary_cols = ['date', 'max_temp', 'average_temperature', 'min_temp',
                                       'max_relative_humidity', 'max_snowfall', 'max_rain',
                                       'max_snow_depth', 'max_windspeed', 'weather_type']
                display_weather_df = weather_df[weather_summary_cols].head(20).copy()
                display_weather_df = display_weather_df.round({'max_temp': 1, 'average_temperature': 1,
                                                             'min_temp': 1, 'max_relative_humidity': 1,
                                                             'max_snowfall': 1, 'max_rain': 1,
                                                             'max_snow_depth': 1, 'max_windspeed': 1})
                st.dataframe(display_weather_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure the duckdb database exists and the dbt models have been run.")
        st.code(f"Full error: {e}")

if __name__ == "__main__":
    main()