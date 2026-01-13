select temperature_2m
from {{ source('1_bronze', 'raw_weather') }}
