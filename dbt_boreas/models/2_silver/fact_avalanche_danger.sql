{{
    config(
        materialized = 'incremental',
        unique_key = ['region_id', 'valid_from', 'valid_to'],
        incremental_strategy = 'merge',
        on_schema_change = 'sync_all_columns'
    )
}}

SELECT 
    reg_id AS registration_id,
    region_id,
    danger_level,
    valid_from,
    valid_to,
    publish_time,
    main_text,
    loaded_at
FROM {{ source('1_bronze', 'avalanche_danger_levels') }}
{% if is_incremental() %}
WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{this}})
{% endif %}