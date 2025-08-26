{{ config(materialized='table') }}

select
    s.seller_id,
    s.seller_city,
    s.seller_state,
    g.latitude,
    g.longitude
from {{ ref('stg_sellers') }} s
left join {{ ref('stg_geolocation') }} g
  on s.seller_zip_code_prefix = g.geolocation_zip_code_prefix