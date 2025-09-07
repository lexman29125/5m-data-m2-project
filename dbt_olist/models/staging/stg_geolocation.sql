{{ config(materialized='view') }}

select
    geolocation_zip_code_prefix,
    avg(cast(geolocation_lat as float64)) as latitude,
    avg(cast(geolocation_lng as float64)) as longitude,
    trim(geolocation_city) as city,
    trim(upper(geolocation_state)) as state,
    current_timestamp as record_loaded_at
from {{ source('raw', 'geolocation') }}
group by
    geolocation_zip_code_prefix,
    city,
    state