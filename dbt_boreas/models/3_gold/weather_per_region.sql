{{
    config(
        materialized='table'
    )
}}

WITH grids AS (
    SELECT 
        *
    FROM {{ ref('dim_grids') }}
),

weather AS (
    SELECT 
        *
    FROM {{ ref('fact_weather') }}
),

daily_aggregation_weather AS (
    SELECT
        grid_id,
        DATE(time) AS "date",
        MAX(temperature_2m) AS max_temp,
        AVG(temperature_2m) AS average_temperature,
        MIN(temperature_2m) AS min_temp,
        MAX(relative_humidity_2m) AS max_relative_humidity,
        AVG(relative_humidity_2m) AS average_relative_humidity,
        MIN(relative_humidity_2m) AS min_relative_humidity,
        MAX(snowfall) AS max_snowfall,
        AVG(snowfall) AS average_snowfall,
        MIN(snowfall) AS min_snowfall,
        MAX(rain) AS max_rain,
        AVG(rain) AS average_rain,
        MIN(rain) AS min_rain,
        MAX(snow_depth) AS max_snow_depth,
        AVG(snow_depth) AS average_snow_depth,
        MIN(snow_depth) AS min_snow_depth,
        MAX(windspeed_10m) AS max_windspeed,
        AVG(windspeed_10m) AS average_windspeed,
        MIN(windspeed_10m) AS min_windspeed,
        MODE(weather_type) AS weather_type
    FROM weather
    GROUP BY  grid_id, DATE(time)
),

daw_with_grid_info AS (
    SELECT 
        *
    FROM daily_aggregation_weather daw
    LEFT JOIN grids g
    ON daw.grid_id = g.id
)


SELECT 
    date,
	max_temp,
	average_temperature,
	min_temp,
	max_relative_humidity,
	average_relative_humidity,
	min_relative_humidity,
	max_snowfall,
	average_snowfall,
	min_snowfall,
	max_rain,
	average_rain,
	min_rain,
	max_snow_depth,
	average_snow_depth,
	min_snow_depth,
	max_windspeed,
	average_windspeed,
	min_windspeed,
	weather_type,
    east_south_lon,
	east_south_lat,
	west_north_lon,
	west_north_lat
FROM daw_with_grid_info