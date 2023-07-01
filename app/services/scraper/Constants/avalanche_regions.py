from dataclasses import dataclass
from typing import List

@dataclass
class AvalancheRegion:
    name: str
    region_id: str
    lat: float
    lon: float


AVALANCHE_REGIONS: List[AvalancheRegion] = [
    AvalancheRegion(name="Trollheimen", region_id="3022", lat=62.800, lon=9.199)
]
