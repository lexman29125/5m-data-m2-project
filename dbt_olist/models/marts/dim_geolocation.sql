{{ config(materialized='table') }}

select distinct
    zip_prefix as geolocation_zip_prefix,
    city,
    state,
    lat,
    lng
from {{ ref('stg_geolocation') }}