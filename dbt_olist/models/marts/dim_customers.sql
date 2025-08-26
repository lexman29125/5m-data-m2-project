{{ config(materialized='table') }}

SELECT DISTINCT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    g.latitude,
    g.longitude
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('stg_geolocation') }} g
  ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix