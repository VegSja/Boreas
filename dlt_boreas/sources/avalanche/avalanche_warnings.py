
import dlt
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterator

from sources.avalanche.avalanche_helper import fetch_avalanche_warnings_data
from src.config.regions import AVALANCHE_REGIONS
from src.models.regions import AvalancheRegion
from exceptions import AvalancheAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


def date_range_chunks(start: date, end: date, chunk_days: int) -> Iterator[tuple[date, date]]:
    """Split a date range into smaller chunks."""
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end)
        yield current, chunk_end
        current = chunk_end + timedelta(days=1)


@dlt.source
def avalanche_warning_source(
    start_date: str = dlt.config.value,
    language_key: str = dlt.config.value,
    api_base_url: str = dlt.config.value,
    request_timeout: int = dlt.config.value,
    chunk_days: int = 30,
    overlap_days: int = 7,
):
    """DLT source for avalanche warning data.
    
    Args:
        start_date: Start date for data collection
        language_key: Language key for API requests
        api_base_url: Base URL for avalanche API
        request_timeout: Request timeout in seconds
        chunk_days: Number of days to fetch per API request
        overlap_days: Number of recent days to always re-fetch for forecast updates
    
    Returns:
        List of dlt resources for avalanche warnings from all regions
    """

    def cap_state_at_today(values):
        if not values:
            return start_date
        
        incoming_values = max(values)
        today = datetime.combine(date.today(), datetime.min.time()).strftime("%Y-%m-%dT%H:%M:%S")
        capped_value = min(incoming_values, today)
        
        return capped_value 

    resources = []
    for region in AVALANCHE_REGIONS:
        def make_avalanche_warning_resource(r: AvalancheRegion = region):

            @dlt.resource(
                table_name="avalanche_danger_levels",
                write_disposition="merge",
                primary_key=['RegId', 'ValidFrom', 'ValidTo'],
                name=f'avalanche_warning_{r.region_id}',
                schema_contract={"tables": "evolve", "columns": "evolve", "data_type": "freeze"}
            )
            def avalanche_warning_resource(
                incremental_start_date: dlt.sources.incremental[str] = dlt.sources.incremental(
                    "ValidFrom", 
                    initial_value=start_date,
                    last_value_func=cap_state_at_today
                )
            ) -> Iterator[Dict[str, Any]]:
                """Fetch avalanche warning data for a specific region.
                
                Yields:
                    Dict containing avalanche warning data
                """
                incremental_date = datetime.strptime(
                    incremental_start_date.last_value, "%Y-%m-%dT%H:%M:%S"
                ).date()
                # Always re-fetch at least the last N days to catch forecast updates
                overlap_date = date.today() - timedelta(days=overlap_days)
                start = min(incremental_date, overlap_date)
                end = date.today() + timedelta(days=4)  # Include forecast days
                
                for chunk_start, chunk_end in date_range_chunks(start, end, chunk_days):
                    logger.info(f"Fetching {r.region_id}: {chunk_start} to {chunk_end}")
                    
                    try:
                        for record in fetch_avalanche_warnings_data(
                            region_id=r.region_id,
                            language_key=language_key,
                            start_date=chunk_start.isoformat(),
                            end_date=chunk_end.isoformat(),
                            api_base_url=api_base_url,
                            request_timeout=request_timeout
                        ):
                            yield record
                        
                    except AvalancheAPIError as e:
                        logger.error(f"Failed at {r.region_id} ({chunk_start} to {chunk_end}): {e}")
                        raise
                        
            return avalanche_warning_resource
        resources.append(make_avalanche_warning_resource())
    return resources