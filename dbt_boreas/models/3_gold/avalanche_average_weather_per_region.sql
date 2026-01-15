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

weather AS (
    SELECT 
        *
    FROM {{ ref('fact_weather') }}
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
),

daily_aggregation_weather AS (
    SELECT
        region_id,
        DATE(time) AS "date",
        MAX(temperature_2m) AS max_temp,
        AVG(temperature_2m) AS average_temperature,
        MIN(temperature_2m) AS min_temp,
        MAX(relative_humidity_2m) AS max_relative_humidity,
        AVG(relative_humidity_2m) AS average_relative_humidity,
        MIN(relative_humidity_2m) AS min_relative_humidity,
        MAX(precipitation) AS max_precipitation,
        AVG(precipitation) AS average_precipitation,
        MIN(precipitation) AS min_precipitation,
        MAX(windspeed_10m) AS max_windspeed,
        AVG(windspeed_10m) AS average_windspeed,
        MIN(windspeed_10m) AS min_windspeed,
        MODE(weather_type) AS weather_type
    FROM weather
    GROUP BY  region_id, DATE(time)
),

total AS (
    SELECT 
        *
    FROM avalanches_with_regions awr
    LEFT JOIN daily_aggregation_weather daw
    ON awr.date = daw.date AND awr.region_id = daw.region_id
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
	west_north_lat,
	max_temp,
	min_temp,
	max_relative_humidity,
	min_relative_humidity,
	max_precipitation,
	min_precipitation,
	max_windspeed,
	min_windspeed,
	weather_type

FROM total