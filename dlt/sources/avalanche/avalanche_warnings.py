
import dlt
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterator

from sources.avalanche.avalanche_helper import fetch_avalanche_warnings_data
from src.config.regions import AVALANCHE_REGIONS
from src.models.regions import AvalancheRegion
from exceptions import AvalancheAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


@dlt.source
def avalanche_warning_source(
    start_date: str = dlt.config.value,
    language_key: str = dlt.config.value,
    api_base_url: str = dlt.config.value,
    request_timeout: int = dlt.config.value
):
    """DLT source for avalanche warning data.
    
    Args:
        start_date: Start date for data collection
        language_key: Language key for API requests
    
    Returns:
        List of dlt resources for avalanche warnings from all regions
    """
    resources = []
    for region in AVALANCHE_REGIONS:
        def make_avalanche_warning_resource(r: AvalancheRegion = region):
            @dlt.resource(
                table_name="avalanche_danger_levels",
                write_disposition="replace",
                primary_key=['RegId', 'ValidFrom', 'ValidTo'],
                name=f'avalanche_warning_{r.region_id}',
                schema_contract={"tables": "evolve", "columns": "evolve", "data_type": "freeze"}
            )
            def avalanche_warning_resource() -> Iterator[Dict[str, Any]]:
                """Fetch avalanche warning data for a specific region.
                
                Yields:
                    Dict containing avalanche warning data
                """
                try:
                    yield from fetch_avalanche_warnings_data(
                        region_id=r.region_id,
                        language_key=language_key,
                        start_date=datetime.strptime(start_date, "%Y-%m-%dT%H:%M").date().isoformat(),
                        end_date=(date.today() + timedelta(days=7)).isoformat(),
                        api_base_url=api_base_url,
                        request_timeout=request_timeout
                    )
                except AvalancheAPIError as e:
                    logger.error(f"Failed to fetch avalanche warning data for {r.name}: {e}")
                    raise
            return avalanche_warning_resource
        resources.append(make_avalanche_warning_resource())
    return resources