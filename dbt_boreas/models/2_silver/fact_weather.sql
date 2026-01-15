{{
    config(
        materialized = 'table'
    )
}}

WITH historic AS (
    SELECT *,
    'historic' AS weather_type
    FROM {{ source('1_bronze', 'weather_historic') }}
    WHERE "time" < today()
), 

forecast AS (
    SELECT *,
    'forecast' AS weather_type
    FROM {{ source('1_bronze', 'weather_forecast') }}
    WHERE "time" > today()
),

unioned AS (
    SELECT *
    FROM historic
    UNION ALL 
    SELECT *
    FROM forecast
)

SELECT 
    time,
    temperature_2m,
    relative_humidity_2m,
    precipitation,
    windspeed_10m,
    loaded_at, --TODO: Needed?
    region_id,
    weather_type,
FROM unioned


