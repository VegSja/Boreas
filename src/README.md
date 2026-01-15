```
██████╗  ██████╗ ██████╗ ███████╗ █████╗ ███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝
██████╔╝██║   ██║██████╔╝█████╗  ███████║███████╗
██╔══██╗██║   ██║██╔══██╗██╔══╝  ██╔══██║╚════██║
██████╔╝╚██████╔╝██║  ██║███████╗██║  ██║███████║
╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝

SHARED LIBRARIES | Platform Configuration & Models
```

# Source Code - Shared Configuration & Models

Enterprise-grade shared Python modules providing configuration management, data models, and utilities across the Boreas avalanche analytics platform. Features comprehensive Norwegian region definitions and standardized data structures.

## Module Architecture

| Component | Purpose | Dependencies | Integration Points |
|-----------|---------|--------------|-------------------|
| **config/regions.py** | Norwegian avalanche region definitions | None | DLT, dbt, Dashboard |
| **models/regions.py** | Data model classes and validation | Python 3.12+ | Cross-platform usage |

### Project Structure
```
src/
├── config/
│   ├── __init__.py                    # Package initialization
│   └── regions.py                     # Avalanche region catalog
├── models/
│   ├── __init__.py                    # Model exports
│   └── regions.py                     # AvalancheRegion data class
└── __init__.py                        # Root package
```

## Norwegian Avalanche Regions (`config/regions.py`)

### Geographic Coverage
Comprehensive catalog of 23 official Norwegian avalanche warning regions with precise geographic boundaries.

| Region Category | Coverage Areas | Region Count |
|----------------|----------------|-------------|
| **Svalbard** | Nordenskiöld Land | 1 |
| **Finnmark** | Finnmarkskysten, Vest-Finnmark | 2 |
| **Troms** | Nord-Troms, Lyngen, Tromsø, Sør-Troms, Indre Troms | 5 |
| **Nordland** | Lofoten, Ofoten, Salten, Svartisen, Helgeland | 5 |
| **Central Norway** | Trollheimen, Romsdal, Sunnmøre | 3 |
| **Western Norway** | Indre Fjordane, Jotunheimen, Sogn, Voss, Hardanger | 5 |
| **Eastern Norway** | Hallingdal, Vest-Telemark, Heiane | 3 |

### Data Structure Specification
```python
AvalancheRegion(
    name="Region Name",              # Official display name
    region_id="3XXX",               # NVE standardized identifier
    west_north_lat=XX.X,           # Northwest boundary latitude
    west_north_lon=XX.X,           # Northwest boundary longitude  
    east_south_lat=XX.X,           # Southeast boundary latitude
    east_south_lon=XX.X            # Southeast boundary longitude
)
```

### Professional Usage
```python
from src.config.regions import AVALANCHE_REGIONS

# Enterprise region access
region_catalog = {r.region_id: r for r in AVALANCHE_REGIONS}
tromsoe = region_catalog.get("3011")

# Geographic calculations
center_point = (tromsoe.center_lat, tromsoe.center_lon)
```

## Data Models (`models/regions.py`)

### AvalancheRegion Class Specification
Enterprise data class representing avalanche warning regions with built-in geographic calculations and validation.

| Attribute | Type | Description | Validation |
|-----------|------|-------------|------------|
| `name` | `str` | Human-readable region name | Required, non-empty |
| `region_id` | `str` | Official NVE identifier | Format: "3XXX" |
| `west_north_lat` | `float` | Northwest boundary latitude | 57.0-81.0°N |
| `west_north_lon` | `float` | Northwest boundary longitude | 4.0-32.0°E |
| `east_south_lat` | `float` | Southeast boundary latitude | 57.0-81.0°N |
| `east_south_lon` | `float` | Southeast boundary longitude | 4.0-32.0°E |

### Computed Properties
```python
@property
def center_lat(self) -> float:
    """Geographic center latitude calculation"""
    return (self.west_north_lat + self.east_south_lat) / 2

@property  
def center_lon(self) -> float:
    """Geographic center longitude calculation"""
    return (self.west_north_lon + self.east_south_lon) / 2
```

### Production Implementation
```python
from src.models.regions import AvalancheRegion

# Enterprise region instantiation
region = AvalancheRegion(
    name="Tromsø",
    region_id="3011",
    west_north_lat=69.8,
    west_north_lon=17.5,
    east_south_lat=69.2,
    east_south_lon=20.5
)

# Geographic boundary calculations
bounds = {
    'north': region.west_north_lat,
    'south': region.east_south_lat,
    'west': region.west_north_lon,
    'east': region.east_south_lon,
    'center': (region.center_lat, region.center_lon)
}
```

## Platform Integration

### Cross-Component Usage
| Component | Integration Purpose | Usage Pattern |
|-----------|-------------------|---------------|
| **DLT Pipelines** | Region data ingestion, API mapping | `from src.config.regions import AVALANCHE_REGIONS` |
| **dbt Models** | Geographic joins, dimension tables | Referenced via bronze layer |
| **Dashboard** | Map visualization, regional filtering | Direct import for coordinates |

### DLT Pipeline Integration
```python
# Region data pipeline implementation
from src.config.regions import AVALANCHE_REGIONS

@dlt.resource(table_name="regions")
def region_data():
    for region in AVALANCHE_REGIONS:
        yield {
            'region_id': region.region_id,
            'name': region.name,
            'center_lat': region.center_lat,
            'center_lon': region.center_lon,
            'boundaries': {
                'north': region.west_north_lat,
                'south': region.east_south_lat,
                'west': region.west_north_lon,
                'east': region.east_south_lon
            }
        }
```

### dbt Model Integration
```sql
-- Example: Regional dimension table
SELECT 
    region_id,
    name,
    center_lat,
    center_lon,
    boundaries
FROM {{ source('1_bronze', 'regions') }}
WHERE region_id IS NOT NULL
```

## Data Validation Framework

### Geographic Validation
```python
def validate_region_bounds(region: AvalancheRegion) -> bool:
    """Enterprise geographic boundary validation"""
    return (
        region.west_north_lat > region.east_south_lat and    # North > South
        region.east_south_lon > region.west_north_lon and    # East > West
        57.0 <= region.east_south_lat <= 81.0 and           # Norway latitude bounds
        4.0 <= region.west_north_lon <= 32.0                 # Norway longitude bounds
    )
```

### Data Quality Checks
```python
def validate_region_catalog() -> list[str]:
    """Comprehensive catalog validation"""
    errors = []
    region_ids = set()
    
    for region in AVALANCHE_REGIONS:
        # Duplicate ID check
        if region.region_id in region_ids:
            errors.append(f"Duplicate region ID: {region.region_id}")
        region_ids.add(region.region_id)
        
        # Geographic validation
        if not validate_region_bounds(region):
            errors.append(f"Invalid bounds for {region.name}")
    
    return errors
```

## Extensibility Framework

### Adding New Regions
```python
# 1. Define new region with validation
new_region = AvalancheRegion(
    name="New Region",
    region_id="3XXX",
    west_north_lat=XX.X,
    west_north_lon=XX.X,
    east_south_lat=XX.X,
    east_south_lon=XX.X
)

# 2. Validate before adding
if validate_region_bounds(new_region):
    AVALANCHE_REGIONS.append(new_region)

# 3. Sync with data pipeline
# Run: cd dlt && uv run python run_dlt_pipelines.py
# Run: cd dbt_boreas && uv run dbt run
```

### Model Extensions
```python
@dataclass
class ExtendedAvalancheRegion(AvalancheRegion):
    """Extended region model with additional properties"""
    elevation_min: float = None
    elevation_max: float = None
    climate_zone: str = None
    population_density: float = None
    
    @property
    def elevation_range(self) -> float:
        if self.elevation_min and self.elevation_max:
            return self.elevation_max - self.elevation_min
        return None
    
    @property
    def risk_category(self) -> str:
        """Calculate risk based on elevation and population"""
        if self.elevation_max and self.elevation_max > 2000:
            return "HIGH" if self.population_density > 10 else "MEDIUM"
        return "LOW"
```

## Testing & Quality Assurance

### Unit Test Framework
```python
import pytest
from src.models.regions import AvalancheRegion
from src.config.regions import AVALANCHE_REGIONS

class TestAvalancheRegion:
    def test_center_calculation_accuracy(self):
        """Test geographic center calculation precision"""
        region = AvalancheRegion("Test", "9999", 70.0, 10.0, 69.0, 11.0)
        assert region.center_lat == 69.5
        assert region.center_lon == 10.5
    
    def test_boundary_validation(self):
        """Test geographic boundary logical consistency"""
        for region in AVALANCHE_REGIONS:
            assert region.west_north_lat > region.east_south_lat
            assert region.east_south_lon > region.west_north_lon
    
    def test_norway_geographic_bounds(self):
        """Test all regions within Norway's geographic boundaries"""
        for region in AVALANCHE_REGIONS:
            assert 57.0 <= region.east_south_lat <= 81.0
            assert 4.0 <= region.west_north_lon <= 32.0

    def test_unique_region_ids(self):
        """Test region ID uniqueness across catalog"""
        region_ids = [r.region_id for r in AVALANCHE_REGIONS]
        assert len(region_ids) == len(set(region_ids))
```

## Dependencies & Requirements

### Technical Dependencies
| Category | Requirement | Version | Purpose |
|----------|------------|---------|---------|
| **Runtime** | Python | 3.12+ | Core language features |
| **Development** | pytest | Latest | Unit testing framework |
| **Integration** | DLT | >= 1.20.0 | Pipeline integration |
| **Integration** | dbt-core | >= 1.11.2 | Model integration |

### Platform Dependencies
- **No external package dependencies** - Pure Python implementation
- **Cross-platform compatibility** - Works on all major operating systems
- **Thread-safe** - Immutable data structures for concurrent access

---

**Enterprise Standards**: Production-grade shared libraries  
**Coverage**: 23 Norwegian avalanche regions  
**Last Updated**: January 2026