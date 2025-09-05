{{ config(materialized='table') }}

select distinct
    s.seller_id,
    s.seller_city,
    s.seller_state,
    g.geolocation_id,
    g.latitude,
    g.longitude,
    current_timestamp as record_loaded_at
from {{ ref('stg_sellers') }} s
left join {{ ref('stg_geolocation') }} g
  on s.seller_zip_code_prefix = g.geolocation_zip_code_prefix
