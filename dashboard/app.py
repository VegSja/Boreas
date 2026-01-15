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
def load_avalanche_weather_data():
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
        west_north_lat,
        max_temp,
        min_temp,
        max_relative_humidity,
        min_relative_humidity,
        max_precipitation,
        min_precipitation,
        max_windspeed,
        min_windspeed,
        weather_type
    FROM "3_gold"."avalanche_average_weather_per_region"
    WHERE date IS NOT NULL
    ORDER BY date DESC, region_name
    """
    return conn.execute(query).df()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def create_grid_coordinates(data):
    """Create grid coordinates for map visualization"""
    grid_data = []
    
    try:
        for _, row in data.iterrows():
            if pd.notna(row['east_south_lon']) and pd.notna(row['west_north_lon']):
                # Create a 3x3 grid within each region's bounds
                lon_range = np.linspace(row['west_north_lon'], row['east_south_lon'], 3)
                lat_range = np.linspace(row['east_south_lat'], row['west_north_lat'], 3)
                
                for lon in lon_range:
                    for lat in lat_range:
                        grid_point = row.copy()
                        grid_point['grid_lon'] = lon
                        grid_point['grid_lat'] = lat
                        # Ensure danger_level is numeric
                        if pd.notna(grid_point['danger_level']):
                            grid_point['danger_level'] = float(grid_point['danger_level'])
                        grid_data.append(grid_point)
        
        return pd.DataFrame(grid_data)
    except Exception as e:
        st.sidebar.write(f"Grid creation error: {e}")
        return pd.DataFrame()  # Return empty dataframe on error

def main():
    st.title("🌨️ Boreas Avalanche & Weather Dashboard")
    st.markdown("Integrated avalanche danger and weather data from Norwegian regions")
    
    # Load data
    try:
        data_df = load_avalanche_weather_data()
        
        if data_df.empty:
            st.warning("No data available. Make sure the dbt models have been run.")
            return
        
        # Data type conversions and cleaning
        try:
            # Convert date column to date type if it's datetime
            if data_df['date'].dtype.name.startswith('datetime'):
                data_df['date'] = data_df['date'].dt.date
            
            # Convert danger_level to numeric, handling any string issues
            if data_df['danger_level'].dtype == 'object':
                # For string columns, first check for problematic values
                problematic_mask = data_df['danger_level'].astype(str).str.len() > 2
                if problematic_mask.any():
                    st.warning(f"Found {problematic_mask.sum()} records with long danger_level values. Removing them.")
                    data_df = data_df[~problematic_mask]
                
                data_df['danger_level'] = pd.to_numeric(data_df['danger_level'], errors='coerce')
            
            # Remove rows with invalid danger levels
            data_df = data_df.dropna(subset=['danger_level'])
            
            if data_df.empty:
                st.warning("No valid data after cleaning. Check data quality.")
                return
                
        except Exception as e:
            st.error(f"Error during data cleaning: {str(e)}")
            return
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Region filter
        available_regions = sorted(data_df['region_name'].dropna().unique())
        selected_regions = st.sidebar.multiselect(
            "Select Regions", 
            available_regions, 
            default=available_regions
        )
        
        # Danger level filter - now handling numeric values
        danger_levels = sorted([int(x) for x in data_df['danger_level'].dropna().unique()])
        selected_danger_levels = st.sidebar.multiselect(
            "Danger Levels",
            danger_levels,
            default=danger_levels
        )
        
        # Filter data by region and danger level only
        filtered_df = data_df[
            (data_df['region_name'].isin(selected_regions)) &
            (data_df['danger_level'].isin(selected_danger_levels))
        ]
        
        if filtered_df.empty:
            st.warning("No data matches your filters.")
            return
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            try:
                avg_danger = filtered_df['danger_level'].astype(float).mean()
                st.metric("Avg Danger Level", f"{avg_danger:.1f}")
            except Exception as e:
                st.metric("Avg Danger Level", "N/A")
                st.sidebar.write(f"Danger level error: {e}")
        
        with col2:
            try:
                avg_temp_range = (filtered_df['max_temp'].mean() + filtered_df['min_temp'].mean()) / 2
                st.metric("Avg Temperature", f"{avg_temp_range:.1f}°C")
            except:
                st.metric("Avg Temperature", "N/A")
        
        with col3:
            try:
                total_precip = filtered_df['max_precipitation'].sum()
                st.metric("Total Max Precipitation", f"{total_precip:.1f}mm")
            except:
                st.metric("Total Max Precipitation", "N/A")
        
        with col4:
            try:
                avg_wind = filtered_df['max_windspeed'].mean()
                st.metric("Avg Max Wind Speed", f"{avg_wind:.1f} m/s")
            except:
                st.metric("Avg Max Wind Speed", "N/A")
        
        # Regional boundary map visualization
        st.subheader("Regional Map - Avalanche Danger & Weather")
        
        # Single date filter for map
        min_date = filtered_df['date'].min()
        max_date = filtered_df['date'].max()
        
        col1, col2 = st.columns([1, 3])
        with col1:
            # Default to today's date, but constrain to available data range
            today = date.today()
            default_date = today if min_date <= today <= max_date else max_date
            
            selected_map_date = st.date_input(
                "Select Date for Map",
                value=default_date,
                min_value=min_date,
                max_value=max_date,
                key="map_date"
            )
        
        # Filter data for the map by selected date
        map_filtered_df = filtered_df[filtered_df['date'] == selected_map_date]
        
        # Get latest data for each region from the selected date
        latest_data = map_filtered_df.groupby('region_id').last().reset_index()
        
        if not latest_data.empty:
            # Create map with region boundary squares
            fig_map = go.Figure()
            
            # Add region squares colored by danger level  
            danger_colors = {1: 'rgba(0,128,0,0.5)', 2: 'rgba(255,255,0,0.5)', 3: 'rgba(255,165,0,0.5)', 4: 'rgba(255,0,0,0.5)', 5: 'rgba(139,0,0,0.5)'}
            
            for _, row in latest_data.iterrows():
                if pd.notna(row['east_south_lon']) and pd.notna(row['west_north_lon']) and pd.notna(row['danger_level']):
                    # Define square corners based on lat/lon bounds
                    lons = [row['west_north_lon'], row['east_south_lon'], row['east_south_lon'], row['west_north_lon'], row['west_north_lon']]
                    lats = [row['west_north_lat'], row['west_north_lat'], row['east_south_lat'], row['east_south_lat'], row['west_north_lat']]
                    
                    color = danger_colors.get(row['danger_level'], 'gray')
                    
                    fig_map.add_trace(go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode='lines',
                        fill='toself',
                        fillcolor=color,
                        line=dict(color='black', width=2),
                        opacity=1.0,
                        hoverinfo='skip',
                        showlegend=False
                    ))
                    
                    # Add grid of invisible points for hover across entire square
                    lat_points = []
                    lon_points = []
                    texts = []
                    
                    # Create a 5x5 grid of hover points across the square
                    lat_range = np.linspace(row['east_south_lat'], row['west_north_lat'], 5)
                    lon_range = np.linspace(row['west_north_lon'], row['east_south_lon'], 5)
                    
                    for lat in lat_range:
                        for lon in lon_range:
                            lat_points.append(lat)
                            lon_points.append(lon)
                            texts.append(row['region_name'])
                    
                    fig_map.add_trace(go.Scattermapbox(
                        lat=lat_points,
                        lon=lon_points,
                        mode='markers',
                        marker=dict(size=15, opacity=0),
                        text=texts,
                        hovertemplate=f'<b>{row["region_name"]}</b><br>' +
                                    f'Danger Level: {row["danger_level"]}<br>' +
                                    f'Temp: {row["max_temp"]:.1f}°C<br>' +
                                    f'Wind: {row["max_windspeed"]:.1f} m/s<br>' +
                                    '<extra></extra>',
                        name=f'{row["region_name"]} (Level {int(row["danger_level"])})',
                        showlegend=False
                    ))
            
            fig_map.update_layout(
                mapbox=dict(
                    style="carto-positron",
                    center=dict(lat=65, lon=15),
                    zoom=4
                ),
                height=600,
                margin={"r":0,"t":0,"l":0,"b":0},
                showlegend=True
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
        
        # Heatmap of danger levels by region
        st.subheader("Danger Level Heatmap by Region")
        
        # Date range filter for heatmap
        col1, col2 = st.columns([1, 3])
        with col1:
            # Default end date to today, start date 30 days before
            today = date.today()
            default_end_date = today if min_date <= today <= max_date else max_date
            default_start_date = min_date
            default_start_date = max(default_start_date, min_date)  # Ensure within available range
            
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
            heatmap_filtered_df = filtered_df[
                (filtered_df['date'] >= start_date) &
                (filtered_df['date'] <= end_date)
            ]
        else:
            heatmap_filtered_df = filtered_df
        
        # Create a copy for heatmap processing
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
        
        # Data summary table
        st.subheader("Recent Data Summary")
        summary_cols = ['date', 'region_name', 'danger_level', 'max_temp', 'min_temp', 
                       'max_precipitation', 'max_windspeed', 'weather_type']
        display_df = filtered_df[summary_cols].head(50).copy()
        display_df = display_df.round({'max_temp': 1, 'min_temp': 1, 'max_precipitation': 1, 'max_windspeed': 1})
        st.dataframe(display_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Make sure the duckdb database exists and the dbt models have been run.")
        st.code(f"Full error: {e}")

if __name__ == "__main__":
    main()