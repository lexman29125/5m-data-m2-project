{{ config(materialized='table') }}

select
    geolocation_zip_code_prefix as zip_prefix,
    latitude,
    longitude,
    city,
    state
from {{ ref('stg_geolocation') }}