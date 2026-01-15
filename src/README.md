# Source Code - Shared Configuration & Models

Shared Python modules containing configuration data, data models, and utilities used across the Boreas platform.

## 📁 Structure

```
src/
├── config/
│   ├── __init__.py
│   └── regions.py              # Avalanche region definitions
├── models/
│   ├── __init__.py
│   └── regions.py              # Data model classes
└── __init__.py
```

## 🗺️ Regional Configuration (`config/regions.py`)

### Avalanche Regions
Comprehensive list of 23 Norwegian avalanche regions with geographic boundaries.

**Coverage Areas**:
- **Svalbard**: Nordenskiöld Land
- **Finnmark**: Finnmarkskysten, Vest-Finnmark  
- **Troms**: Nord-Troms, Lyngen, Tromsø, Sør-Troms, Indre Troms
- **Nordland**: Lofoten og Vesterålen, Ofoten, Salten, Svartisen, Helgeland
- **Trøndelag**: Trollheimen
- **Møre og Romsdal**: Romsdal, Sunnmøre
- **Vestland**: Indre Fjordane, Jotunheimen, Indre Sogn, Voss, Hardanger
- **Innlandet**: Hallingdal
- **Telemark**: Vest-Telemark
- **Rogaland**: Heiane

### Region Data Structure
Each region contains:
```python
AvalancheRegion(
    name="Region Name",          # Display name
    region_id="3XXX",           # Official NVE region ID
    west_north_lat=XX.X,        # Northwest corner latitude
    west_north_lon=XX.X,        # Northwest corner longitude  
    east_south_lat=XX.X,        # Southeast corner latitude
    east_south_lon=XX.X         # Southeast corner longitude
)
```

### Usage Example
```python
from src.config.regions import AVALANCHE_REGIONS

# Access all regions
for region in AVALANCHE_REGIONS:
    print(f"{region.name}: {region.region_id}")

# Find specific region
tromsoe = next(r for r in AVALANCHE_REGIONS if r.name == "Tromsø")
print(f"Center: {tromsoe.center_lat}, {tromsoe.center_lon}")
```

## 🔧 Data Models (`models/regions.py`)

### AvalancheRegion Class
Data class representing an avalanche warning region with geographic boundaries.

**Attributes**:
- `name: str` - Human-readable region name
- `region_id: str` - Official NVE identifier  
- `west_north_lat: float` - Northwest boundary latitude
- `west_north_lon: float` - Northwest boundary longitude
- `east_south_lat: float` - Southeast boundary latitude
- `east_south_lon: float` - Southeast boundary longitude

**Properties**:
```python
@property
def center_lat(self) -> float:
    """Calculate region center latitude"""
    return (self.west_north_lat + self.east_south_lat) / 2

@property  
def center_lon(self) -> float:
    """Calculate region center longitude"""
    return (self.west_north_lon + self.east_south_lon) / 2
```

### Usage Examples

**Create Region Instance**:
```python
from src.models.regions import AvalancheRegion

region = AvalancheRegion(
    name="Tromsø",
    region_id="3011",
    west_north_lat=69.8,
    west_north_lon=17.5,
    east_south_lat=69.2,
    east_south_lon=20.5
)
```

**Calculate Geographic Properties**:
```python
# Get region center point
center = (region.center_lat, region.center_lon)

# Calculate region bounds
bounds = {
    'north': region.west_north_lat,
    'south': region.east_south_lat,
    'west': region.west_north_lon,
    'east': region.east_south_lon
}
```

## 🔗 Integration Points

### DLT Pipelines
- **Region Pipeline**: Loads region data into bronze layer
- **Avalanche Pipeline**: Uses region IDs for API calls
- **Weather Pipeline**: Maps weather data to regions

**Example Usage**:
```python
# In DLT source
from src.config.regions import AVALANCHE_REGIONS

@dlt.resource
def region_data():
    for region in AVALANCHE_REGIONS:
        yield {
            'region_id': region.region_id,
            'name': region.name,
            'center_lat': region.center_lat,
            'center_lon': region.center_lon,
            # ... other fields
        }
```

### dbt Models
- **Region Dimension**: Creates `dim_regions` table
- **Geographic Joins**: Links weather/avalanche data by region
- **Boundary Calculations**: Uses lat/lon for mapping

### Dashboard
- **Map Visualization**: Renders region boundaries as squares
- **Geographic Filtering**: Regional data selection
- **Coordinate Display**: Shows hover information

## 📊 Data Validation

### Geographic Bounds Validation
```python
def validate_region_bounds(region: AvalancheRegion) -> bool:
    """Validate geographic boundaries are logical"""
    return (
        region.west_north_lat > region.east_south_lat and  # North > South
        region.east_south_lon > region.west_north_lon      # East > West
    )
```

### Coordinate Range Validation  
```python
def validate_norway_bounds(region: AvalancheRegion) -> bool:
    """Validate coordinates are within Norway's bounds"""
    return (
        57.0 <= region.east_south_lat <= 81.0 and     # Latitude range
        4.0 <= region.west_north_lon <= 32.0          # Longitude range  
    )
```

## 🔧 Extension Points

### Adding New Regions
1. **Define Region**:
```python
new_region = AvalancheRegion(
    name="New Region",
    region_id="3XXX", 
    west_north_lat=XX.X,
    west_north_lon=XX.X,
    east_south_lat=XX.X,
    east_south_lon=XX.X
)
```

2. **Add to Configuration**:
```python
# In src/config/regions.py
AVALANCHE_REGIONS.append(new_region)
```

3. **Update Data Pipeline**:
- Run DLT region pipeline to sync changes
- Execute dbt models to update dimension table

### Custom Region Properties
Extend the `AvalancheRegion` class:
```python
@dataclass
class ExtendedAvalancheRegion(AvalancheRegion):
    elevation_min: float = None
    elevation_max: float = None
    climate_zone: str = None
    
    @property
    def elevation_range(self) -> float:
        if self.elevation_min and self.elevation_max:
            return self.elevation_max - self.elevation_min
        return None
```

## 📚 Dependencies

**Internal**:
- Used by DLT pipelines (`dlt/sources/`)
- Referenced in dbt models (`dbt_boreas/models/`)
- Imported by dashboard (`dashboard/app.py`)

**External**:
- Python 3.12+ (dataclasses)
- No external package dependencies

## 🧪 Testing

### Unit Tests Example
```python
import pytest
from src.models.regions import AvalancheRegion
from src.config.regions import AVALANCHE_REGIONS

def test_region_center_calculation():
    region = AvalancheRegion("Test", "9999", 70.0, 10.0, 69.0, 11.0)
    assert region.center_lat == 69.5
    assert region.center_lon == 10.5

def test_all_regions_valid():
    for region in AVALANCHE_REGIONS:
        assert region.west_north_lat > region.east_south_lat
        assert region.east_south_lon > region.west_north_lon
```

This shared configuration ensures consistent regional data across all platform components.