import math
from typing import List
from src.models.regions import WeatherGridSquare


def generate_norway_weather_grids() -> List[WeatherGridSquare]:
    """Generate 100x100km weather grid squares covering Norway.
    
    Norway extends approximately:
    - Latitude: 58°N to 71°N (about 1,440 km)
    - Longitude: 4.5°E to 31°E (varies by latitude due to convergence)
    
    Returns:
        List of WeatherGridSquare objects covering Norway
    """
    grids = []
    
    # Norway bounds
    min_lat = 58.0
    max_lat = 71.0
    min_lon = 4.5
    max_lon = 31.0
    
    # Grid size in degrees (approximately 100km)
    lat_step = 100 / 111.0  # ~0.9 degrees latitude
    
    row = 1
    lat = min_lat
    
    while lat < max_lat:
        # Calculate longitude step based on current latitude (accounts for convergence)
        lon_step = 100 / (111.0 * math.cos(math.radians(lat + lat_step/2)))
        
        col = 1
        lon = min_lon
        
        while lon < max_lon:
            # Define grid square bounds
            north_lat = lat + lat_step
            south_lat = lat
            west_lon = lon
            east_lon = lon + lon_step
            
            # Only include squares that overlap with Norway's approximate bounds
            if (south_lat <= 71.0 and north_lat >= 58.0 and 
                west_lon <= 31.0 and east_lon >= 4.5):
                
                grid_id = f"WG_{row:03d}_{col:03d}"
                
                grid = WeatherGridSquare(
                    grid_id=grid_id,
                    west_north_lat=north_lat,
                    west_north_lon=west_lon,
                    east_south_lat=south_lat,
                    east_south_lon=east_lon
                )
                grids.append(grid)
            
            lon += lon_step
            col += 1
        
        lat += lat_step
        row += 1
    
    return grids


# Generate the grid squares
WEATHER_GRID_SQUARES: List[WeatherGridSquare] = generate_norway_weather_grids()