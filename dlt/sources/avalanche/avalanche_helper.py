"""Helper functions for avalanche data processing."""
from typing import Any, Dict, Iterator
from dlt.sources.helpers import requests

from exceptions import AvalancheAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


def fetch_avalanche_warnings_data(
    region_id: str,
    language_key: str,
    start_date: str,
    end_date: str,
    api_base_url: str,
    request_timeout: int = 30
) -> Iterator[Dict[str, Any]]:
    """Fetch avalanche warnings data from NVE API.
    
    Args:
        region_id: Avalanche region identifier
        language_key: Language key for API (1 for Norwegian, 2 for English)
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        api_base_url: Base URL for avalanche API
        request_timeout: Request timeout in seconds
        
    Yields:
        Dict containing avalanche warning records
        
    Raises:
        AvalancheAPIError: If API request fails or returns invalid data
    """
    url = (
        f"{api_base_url}/"
        f"AvalancheWarningByRegion/Simple/"
        f"{region_id}/{language_key}/{start_date}/{end_date}"
    )
    
    try:
        logger.info(f"Fetching avalanche warnings for region {region_id} from {start_date} to {end_date}")
        response = requests.get(url, timeout=request_timeout)
        response.raise_for_status()
        
        data = response.json()
        if not isinstance(data, list):
            raise AvalancheAPIError(f"Invalid response format from avalanche API for region {region_id}")
            
        record_count = 0
        for record in data:
            record_count += 1
            yield record
            
        logger.info(f"Successfully processed {record_count} avalanche warning records for region {region_id}")
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch avalanche warnings for region {region_id}: {e}"
        logger.error(error_msg)
        raise AvalancheAPIError(error_msg) from e
    except (ValueError, TypeError) as e:
        error_msg = f"Failed to process avalanche warnings data for region {region_id}: {e}"
        logger.error(error_msg)
        raise AvalancheAPIError(error_msg) from e