{{
    config(
        materialized = 'incremental',
        unique_key = ['time', 'grid_id'],
        incremental_strategy = 'merge',
        on_schema_change = 'sync_all_columns'
    )
}}

WITH historic AS (
    SELECT 
        *,
        'historic' AS weather_type
    FROM {{ source('1_bronze', 'weather_historic') }}
    WHERE "time" < today()
    {% if is_incremental() %}
        AND loaded_at > (SELECT MAX(loaded_at) FROM {{this}})
    {% endif %}
), 

forecast AS (
    SELECT 
        *,
        'forecast' AS weather_type
    FROM {{ source('1_bronze', 'weather_forecast') }}
    WHERE "time" > today()
    {% if is_incremental() %}
        AND loaded_at > (SELECT MAX(loaded_at) FROM {{this}})
    {% endif %}
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
    snowfall,
    rain,
    snow_depth,
    windspeed_10m,
    loaded_at, 
    grid_id,
    weather_type
FROM unioned


