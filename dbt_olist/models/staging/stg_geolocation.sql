{{ config(materialized='view') }}

select
    geolocation_zip_code_prefix,
    cast(geolocation_lat as float64) as latitude,
    cast(geolocation_lng as float64) as longitude,
    trim(geolocation_city) as city,
    trim(upper(geolocation_state)) as state,
    current_timestamp as record_loaded_at
from {{ source('raw', 'geolocation') }}
