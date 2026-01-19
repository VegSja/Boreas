import dlt
from typing import Dict, List, Any
from dataclasses import asdict

from src.config.weather_grids import WEATHER_GRID_SQUARES
from src.models.regions import WeatherGridSquare


@dlt.source
def weather_grids_source():
    """DLT source for weather grid squares reference data."""

    @dlt.resource(
        table_name="weather_grids",
        write_disposition="replace",  # Always replace to ensure data consistency
        primary_key="grid_id",
        schema_contract={"tables": "evolve", "columns": "evolve", "data_type": "freeze"}
    )
    def weather_grids_resource() -> List[Dict[str, Any]]:
        """Load weather grid squares reference data.

        Yields:
            List of dictionaries containing grid data with calculated center coordinates
        """
        grids_data = []

        for grid in WEATHER_GRID_SQUARES:
            # Convert dataclass to dict and add calculated fields
            grid_dict = asdict(grid)
            grid_dict['center_lat'] = grid.center_lat
            grid_dict['center_lon'] = grid.center_lon
            grids_data.append(grid_dict)

        return grids_data

    return weather_grids_resource