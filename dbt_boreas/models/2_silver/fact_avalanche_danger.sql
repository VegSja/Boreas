{{
    config(
        materialized = 'table'
    )
}}

SELECT 
    reg_id AS registration_id,
    region_id,
    danger_level,
    valid_from,
    valid_to,
    publish_time,
    main_text
FROM {{ source('1_bronze', 'avalanche_danger_levels') }}