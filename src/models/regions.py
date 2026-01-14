from dataclasses import dataclass


@dataclass
class AvalancheRegion:
    name: str
    region_id: str
    west_north_lat: float
    west_north_lon: float
    east_south_lat: float
    east_south_lon: float

    @property
    def center_lat(self) -> float:
        return (self.west_north_lat + self.east_south_lat) / 2

    @property
    def center_lon(self) -> float:
        return (self.west_north_lon + self.east_south_lon) / 2
