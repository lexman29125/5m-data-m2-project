{{ config(materialized='view') }}

select
    cast(geolocation_zip_code_prefix as string) as geolocation_zip_code_prefix,
    avg(cast(geolocation_lat as float64)) as latitude,
    avg(cast(geolocation_lng as float64)) as longitude,
    any_value(geolocation_city) as city,
    any_value(geolocation_state) as state
from {{ source('raw', 'geolocation') }}
where geolocation_zip_code_prefix is not null
group by geolocation_zip_code_prefix