{{
    config(
        materialized='table'
    )
}}

WITH raw_regions AS (
    SELECT *
    FROM {{ source('1_bronze', 'avalanche_regions' )}}
)

SELECT 
    region_id,
    "name",
    east_south_lon,
    east_south_lat,
    west_north_lon,
    west_north_lat
FROM raw_regions