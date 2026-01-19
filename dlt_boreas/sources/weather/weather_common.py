from dlt.sources.helpers import requests
from datetime import datetime, timezone
from typing import Iterator, Dict, Any

from src.models.regions import WeatherGridSquare
from exceptions import WeatherAPIError
from utils.logging import setup_logger

logger = setup_logger(__name__)


def fetch_weather_data(
    url: str, 
    params: Dict[str, Any], 
    region: WeatherGridSquare,
    request_timeout: int = 30
) -> Iterator[Dict[str, Any]]:
    """Fetch and process weather data from Open Meteo API.
    
    Args:
        url: API endpoint URL
        params: Request parameters
        region: Weather grid square information
        request_timeout: Request timeout in seconds
        
    Yields:
        Dict containing weather data records
        
    Raises:
        WeatherAPIError: If API request fails or returns invalid data
    """
    try:
        logger.info(f"Fetching weather data for grid {region.grid_id} from {url}")
        response = requests.get(url, params=params, timeout=request_timeout)
        response.raise_for_status()
        
        data = response.json()
        if 'hourly' not in data:
            raise WeatherAPIError(f"Invalid response format from weather API for grid {region.grid_id}")
            
        hourly = data["hourly"]
        loaded_at = datetime.now(timezone.utc).isoformat()
        
        record_count = 0
        for i in range(len(hourly["time"])):
            record = {key: hourly[key][i] for key in hourly.keys()}
            record["loaded_at"] = loaded_at
            record['grid_id'] = region.grid_id
            record_count += 1
            yield record
            
        logger.info(f"Successfully processed {record_count} weather records for grid {region.grid_id}")
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch weather data for grid {region.grid_id}: {e}"
        logger.error(error_msg)
        raise WeatherAPIError(f"Failed to process weather data for grid {region.grid_id}")
    except (KeyError, ValueError) as e:
        error_msg = f"Failed to process weather data for grid {region.grid_id}: {e}"
        logger.error(error_msg)
        raise WeatherAPIError(f"Failed to process weather data for grid {region.grid_id}")