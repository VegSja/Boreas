{{
    config(
        materialized = 'table'
    )
}}

WITH historic AS (
    SELECT *,
    'historic' AS type
    FROM {{ source('1_bronze', 'weather_historic') }}
), 

forecast AS (
    SELECT *,
    'forecast' AS type
    FROM {{ source('1_bronze', 'weather_forecast') }}
) 

SELECT *
FROM historic
UNION ALL 
SELECT *
FROM forecast