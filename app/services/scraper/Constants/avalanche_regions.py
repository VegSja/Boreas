from dataclasses import dataclass
from typing import List


@dataclass
class AvalancheRegion:
    name: str
    region_id: str
    lat: float
    lon: float


AVALANCHE_REGIONS: List[AvalancheRegion] = [
    AvalancheRegion(name="Svalbar øst", region_id="3001", lat=79.6098, lon=24.849),
    AvalancheRegion(name="Svalbar vest", region_id="3002", lat=78.855, lon=12.0168),
    AvalancheRegion(name="Nordenskiold Land", region_id="3003", lat=77.906, lon=15.182),
    AvalancheRegion(name="Svalbar sør", region_id="3004", lat=76.763, lon=16.675),
    AvalancheRegion(name="Øst-Finnmark", region_id="3005", lat=70.221, lon=29.2843),
    AvalancheRegion(name="Finnmarkskysten", region_id="3006", lat=70.878, lon=24.629),
    AvalancheRegion(name="Nord-Troms", region_id="3009", lat=70.6290, lon=22.928),
    AvalancheRegion(name="Lyngen", region_id="3010", lat=69.736, lon=20.103),
    AvalancheRegion(name="Trømsø", region_id="3011", lat=69.673, lon=18.957),
    AvalancheRegion(name="Lofoten og Vesterålen", region_id="3014", lat=68.182, lon=13.736),
    AvalancheRegion(name="Ofoten", region_id="3015", lat=68.314, lon=16.342),
    AvalancheRegion(name="Salten", region_id="3016", lat=67.339, lon=14.560),
    AvalancheRegion(name="Svartisen", region_id="3017", lat=66.708, lon=13.994),
    AvalancheRegion(name="Helgeland", region_id="3018", lat=65.818, lon=13.289),
    AvalancheRegion(name="Trollheimen", region_id="3022", lat=62.800, lon=9.199),
    AvalancheRegion(name="Romsdal", region_id="3023", lat=62.509, lon=7.2356),
    AvalancheRegion(name="Sunnmøre", region_id="3023", lat=61.956, lon=6.001),
    AvalancheRegion(name="Jotunheimen", region_id="3028", lat=61.631, lon=8.292),
    AvalancheRegion(name="Voss", region_id="3031", lat=60.6242, lon=6.439),
    AvalancheRegion(name="Hallingdal", region_id="3032", lat=60.659, lon=9.05),
    AvalancheRegion(name="Hardanger", region_id="3034", lat=60.230, lon=6.824),
    AvalancheRegion(name="Vest-Telemark", region_id="3035", lat=59.343, lon=7.929),
    AvalancheRegion(name="Heiane", region_id="3035", lat=59.762, lon=5.459),
]
