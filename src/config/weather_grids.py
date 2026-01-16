import math
from typing import List
from src.models.regions import WeatherGridSquare


def is_within_norway(center_lat: float, center_lon: float) -> bool:
    """Check if a grid center point is within Norway's borders (inland/coastal).
    
    This uses detailed latitude-based longitude boundaries to exclude:
    - Sweden and Finland (east)
    - Norwegian Sea (west) - keeping only inland areas or one coastal square
    Norway's eastern border varies significantly by latitude.
    
    Args:
        center_lat: Center latitude of the grid
        center_lon: Center longitude of the grid
        
    Returns:
        True if the point is within Norway, False otherwise
    """
    # Latitude bounds
    if center_lat < 57.9 or center_lat > 71.2:
        return False
    
    # Detailed western bounds by latitude (exclude Norwegian Sea)
    # Allows one coastal square or inland only
    if center_lat < 59.0:
        # South: Oslo region - extend coverage westward to include full southwest
        min_lon = 4.0
    elif center_lat < 60.0:
        # Southeast: Kristiansand area - extend to cover southwest coast
        min_lon = 4.5
    elif center_lat < 61.0:
        # South-central: Stavanger area - keep one coastal square
        min_lon = 5.0
    elif center_lat < 63.0:
        # West-central: Bergen area - keep coastal access
        min_lon = 4.8
    elif center_lat < 65.0:
        # Central: Trondheim area
        min_lon = 6.0
    elif center_lat < 67.0:
        # North: Troms coast - reduce northwest coverage
        min_lon = 10.0
    elif center_lat < 69.0:
        # Northern Finnmark: reduce northwest coverage
        min_lon = 10.0
    else:
        # Far north: reduce northwest coverage
        min_lon = 10.0
    
    # Detailed eastern bounds by latitude to exclude Sweden and Finland
    if center_lat < 59.0:
        max_lon = 12.0
    elif center_lat < 60.0:
        max_lon = 13.0
    elif center_lat < 61.0:
        max_lon = 13.5
    elif center_lat < 62.0:
        max_lon = 15.0
    elif center_lat < 63.0:
        max_lon = 16.0
    elif center_lat < 64.0:
        max_lon = 18.0
    elif center_lat < 65.0:
        max_lon = 23.0
    elif center_lat < 66.0:
        max_lon = 25.0
    elif center_lat < 67.0:
        max_lon = 27.0
    elif center_lat < 68.0:
        max_lon = 28.5
    elif center_lat < 69.0:
        max_lon = 29.0
    elif center_lat < 70.0:
        max_lon = 30.0
    else:
        max_lon = 31.0
    
    return min_lon <= center_lon <= max_lon


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
            
            # Calculate grid center point
            center_lat = (south_lat + north_lat) / 2
            center_lon = (west_lon + east_lon) / 2
            
            # Only include squares that are within Norway
            if is_within_norway(center_lat, center_lon):
                
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