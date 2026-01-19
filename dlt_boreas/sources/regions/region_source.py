import dlt
from typing import Dict, List, Any
from dataclasses import asdict

from src.config.regions import AVALANCHE_REGIONS
from src.models.regions import AvalancheRegion


@dlt.source
def regions_source():
    """DLT source for avalanche regions reference data."""

    @dlt.resource(
        table_name="avalanche_regions",
        write_disposition="replace",  # Always replace to ensure data consistency
        primary_key="region_id",
        schema_contract={"tables": "evolve", "columns": "evolve", "data_type": "freeze"}
    )
    def avalanche_regions_resource() -> List[Dict[str, Any]]:
        """Load avalanche regions reference data.

        Yields:
            List of dictionaries containing region data with calculated center coordinates
        """
        regions_data = []

        for region in AVALANCHE_REGIONS:
            # Convert dataclass to dict and add calculated fields
            region_dict = asdict(region)
            region_dict['center_lat'] = region.center_lat
            region_dict['center_lon'] = region.center_lon
            regions_data.append(region_dict)

        return regions_data

    return avalanche_regions_resource