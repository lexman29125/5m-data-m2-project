{{ config(materialized='table') }}

with c as (
  select * from {{ ref('stg_customers') }}
),
geo as (
  select zip_prefix, city, state, lat, lng from {{ ref('stg_geolocation') }}
)
select distinct
    c.customer_id,
    c.customer_unique_id,
    coalesce(geo.city, c.customer_city) as customer_city,
    coalesce(geo.state, c.customer_state) as customer_state,
    geo.lat as latitude,
    geo.lng as longitude
from c
left join geo on c.customer_zip_code_prefix = geo.zip_prefix