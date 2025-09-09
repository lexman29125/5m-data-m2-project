{{ config(materialized='table') }}

SELECT DISTINCT
    c.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    g.geolocation_zip_code_prefix,  
    g.latitude,
    g.longitude,
    current_timestamp AS record_loaded_at
FROM {{ ref('stg_customers') }} c
LEFT JOIN {{ ref('dim_geolocation') }} g
  ON c.customer_zip_code_prefix = g.geolocation_zip_code_prefix