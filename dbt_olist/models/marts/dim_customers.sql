{{ config(materialized='table') }}

select
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    g.latitude,
    g.longitude
from {{ ref('stg_customers') }} c
left join {{ ref('stg_geolocation') }} g
  on c.customer_zip_code_prefix = g.geolocation_zip_code_prefix