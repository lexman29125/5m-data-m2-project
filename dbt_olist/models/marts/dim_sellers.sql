{{ config(materialized='table') }}

with s as (
  select * from {{ ref('stg_sellers') }}
),
geo as (
  select zip_prefix, city, state, lat, lng from {{ ref('stg_geolocation') }}
)
select distinct
    s.seller_id,
    coalesce(geo.city, s.seller_city) as seller_city,
    coalesce(geo.state, s.seller_state) as seller_state,
    geo.lat as latitude,
    geo.lng as longitude
from s
left join geo on s.seller_zip_code_prefix = geo.zip_prefix