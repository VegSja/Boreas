
from datetime import date, datetime, timedelta
from typing import Any, Dict, Iterator
import dlt
from sources.avalanche.avalanche_helper import fetch_avalanche_warnings_data
from sources.weather.weather_historic import START_DATE
from src.config.regions import AVALANCHE_REGIONS
from src.models.regions import AvalancheRegion


@dlt.source
def avalanche_warning_source():
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
            def avalanche_warning_resource(
            ) -> Iterator[Dict[str, Any]]:
                LANGUAGE_KEY = '1'

                try:
                    yield from fetch_avalanche_warnings_data(
                        region_id=r.region_id,
                        language_key=LANGUAGE_KEY,
                        start_date=datetime.strptime(START_DATE, "%Y-%m-%dT%H:%M").date().isoformat(),
                        end_date=(date.today() + timedelta(days=7)).isoformat(),
                    )
                except Exception as e:
                    print(f"Failed to fetch historic data for {r.name}: {e}")
            return avalanche_warning_resource
        resources.append(make_avalanche_warning_resource())
    return resources
    
    