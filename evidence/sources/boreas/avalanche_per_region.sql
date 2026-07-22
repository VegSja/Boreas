select
    date::date            as date,
    registration_id,
    region_id,
    region_name,
    try_cast(danger_level as integer) as danger_level,
    valid_from,
    valid_to,
    main_text,
    east_south_lon,
    east_south_lat,
    west_north_lon,
    west_north_lat,
    (east_south_lat + west_north_lat) / 2.0 as center_lat,
    (east_south_lon + west_north_lon) / 2.0 as center_lon
from "3_gold"."avalanche_per_region"
where date is not null
  and try_cast(danger_level as integer) is not null
