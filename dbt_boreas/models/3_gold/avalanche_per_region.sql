{{
    config(
        materialized='table'
    )
}}

WITH regions AS (
    SELECT 
        *
    FROM {{ ref('dim_regions') }}
),

avalanches AS (
    SELECT 
        *
    FROM {{ ref('fact_avalanche_danger' )}}
),

avalanches_with_regions AS (
    SELECT
        DATE(valid_from) AS "date",
        a.*,
        r.name AS region_name,
        r.region_id,
        r.center_lat,
        r.center_lon,
        r.east_south_lon,
        r.east_south_lat,
        r.west_north_lon,
        r.west_north_lat
    FROM avalanches a
    LEFT JOIN regions r
    ON a.region_id = r.region_id
)

SELECT 
    date,
    registration_id,
    region_id,
    region_name,
    danger_level,
    valid_from,
    valid_to,
    main_text,
    east_south_lon,
	east_south_lat,
	west_north_lon,
	west_north_lat
FROM avalanches_with_regions