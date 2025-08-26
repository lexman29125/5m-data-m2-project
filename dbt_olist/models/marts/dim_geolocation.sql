{{ config(materialized='table') }}

select
    geolocation_zip_code_prefix,
    latitude,
    longitude,
    city,
    state
from {{ ref('stg_geolocation') }}
where geolocation_zip_code_prefix is not null