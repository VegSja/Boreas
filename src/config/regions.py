from dataclasses import dataclass
from typing import List

from src.models.regions import AvalancheRegion

AVALANCHE_REGIONS: List[AvalancheRegion] = [
    # Svalbard regions
    AvalancheRegion(
        name="Nordenskiöld Land", region_id="3003",
        west_north_lat=78.2, west_north_lon=14.5,
        east_south_lat=77.6, east_south_lon=17.0
    ),
    
    # Finnmark regions  
    AvalancheRegion(
        name="Finnmarkskysten", region_id="3006", 
        west_north_lat=71.2, west_north_lon=23.0,
        east_south_lat=70.4, east_south_lon=31.0
    ),
    AvalancheRegion(
        name="Vest-Finnmark", region_id="3007",
        west_north_lat=71.0, west_north_lon=20.0,
        east_south_lat=68.8, east_south_lon=24.0
    ),
    
    # Troms regions
    AvalancheRegion(
        name="Nord-Troms", region_id="3009",
        west_north_lat=70.8, west_north_lon=18.5,
        east_south_lat=69.8, east_south_lon=24.0
    ),
    AvalancheRegion(
        name="Lyngen", region_id="3010",
        west_north_lat=69.9, west_north_lon=19.5,
        east_south_lat=69.4, east_south_lon=21.0
    ),
    AvalancheRegion(
        name="Tromsø", region_id="3011", 
        west_north_lat=69.8, west_north_lon=17.5,
        east_south_lat=69.2, east_south_lon=20.5
    ),
    AvalancheRegion(
        name="Sør-Troms", region_id="3012",
        west_north_lat=69.5, west_north_lon=17.0,
        east_south_lat=68.7, east_south_lon=21.0
    ),
    AvalancheRegion(
        name="Indre Troms", region_id="3013",
        west_north_lat=69.2, west_north_lon=18.0,
        east_south_lat=68.5, east_south_lon=22.0
    ),
    
    # Nordland regions
    AvalancheRegion(
        name="Lofoten og Vesterålen", region_id="3014",
        west_north_lat=68.9, west_north_lon=12.0,
        east_south_lat=67.8, east_south_lon=15.5
    ),
    AvalancheRegion(
        name="Ofoten", region_id="3015",
        west_north_lat=68.6, west_north_lon=15.5,
        east_south_lat=67.8, east_south_lon=18.5
    ),
    AvalancheRegion(
        name="Salten", region_id="3016",
        west_north_lat=67.8, west_north_lon=13.5,
        east_south_lat=66.8, east_south_lon=16.5
    ),
    AvalancheRegion(
        name="Svartisen", region_id="3017", 
        west_north_lat=67.0, west_north_lon=13.0,
        east_south_lat=66.2, east_south_lon=15.5
    ),
    AvalancheRegion(
        name="Helgeland", region_id="3018",
        west_north_lat=66.5, west_north_lon=12.0,
        east_south_lat=65.2, east_south_lon=15.0
    ),
    
    # Trøndelag regions
    AvalancheRegion(
        name="Trollheimen", region_id="3022",
        west_north_lat=62.97, west_north_lon=8.68,
        east_south_lat=62.59, east_south_lon=9.70
    ),
    
    # Møre og Romsdal
    AvalancheRegion(
        name="Romsdal", region_id="3023",
        west_north_lat=62.8, west_north_lon=6.5,
        east_south_lat=62.0, east_south_lon=8.5
    ),
    AvalancheRegion(
        name="Sunnmøre", region_id="3024",
        west_north_lat=62.5, west_north_lon=5.5,
        east_south_lat=61.7, east_south_lon=8.0
    ),
    
    # Sogn og Fjordane / Vestland
    AvalancheRegion(
        name="Indre Fjordane", region_id="3026", 
        west_north_lat=61.8, west_north_lon=5.0,
        east_south_lat=60.8, east_south_lon=8.5
    ),
    AvalancheRegion(
        name="Jotunheimen", region_id="3028",
        west_north_lat=61.8, west_north_lon=7.5,
        east_south_lat=61.2, east_south_lon=9.0  
    ),
    AvalancheRegion(
        name="Indre Sogn", region_id="3029",
        west_north_lat=61.4, west_north_lon=6.5,
        east_south_lat=60.6, east_south_lon=8.5
    ),
    AvalancheRegion(
        name="Voss", region_id="3031",
        west_north_lat=60.8, west_north_lon=6.0,
        east_south_lat=60.2, east_south_lon=7.5
    ),
    
    # Buskerud/Innlandet
    AvalancheRegion(
        name="Hallingdal", region_id="3032",
        west_north_lat=61.0, west_north_lon=7.5,
        east_south_lat=60.2, east_south_lon=10.0
    ),
    
    # Hardanger
    AvalancheRegion(
        name="Hardanger", region_id="3034", 
        west_north_lat=60.8, west_north_lon=6.0,
        east_south_lat=59.8, east_south_lon=8.0
    ),
    
    # Telemark
    AvalancheRegion(
        name="Vest-Telemark", region_id="3035",
        west_north_lat=59.8, west_north_lon=7.0,
        east_south_lat=59.0, east_south_lon=9.0
    ),
    
    # Rogaland  
    AvalancheRegion(
        name="Heiane", region_id="3037",
        west_north_lat=59.9, west_north_lon=5.0,
        east_south_lat=59.2, east_south_lon=6.5
    ),
]