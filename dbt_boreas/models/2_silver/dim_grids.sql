{{
    config(
        materialized='table'
    )
}}

WITH raw_grids AS (
    SELECT *
    FROM {{ source('1_bronze', 'weather_grids' )}}
)

SELECT 
    grid_id AS id,
    east_south_lon,
    east_south_lat,
    west_north_lon,
    west_north_lat,
    center_lat,
    center_lon
FROM raw_grids