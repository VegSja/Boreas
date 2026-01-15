{{
    config(
        materialized = 'table'
    )
}}

SELECT * 
FROM {{ source('1_bronze', 'avalanche_danger_levels') }}