{{ config(materialized='table') }}

select
    -- {{ dbt_utils.generate_surrogate_key(['geolocation_zip_code_prefix']) }} as geolocation_id,
    geolocation_zip_code_prefix,
    avg(latitude) as latitude,          -- averages the already averaged values from stg_geolocation
    avg(longitude) as longitude,
    min(city) as city,                  -- pick one city deterministically
    min(state) as state,                -- pick one state deterministically
    current_timestamp as record_loaded_at
from {{ ref('stg_geolocation') }}
group by geolocation_zip_code_prefix