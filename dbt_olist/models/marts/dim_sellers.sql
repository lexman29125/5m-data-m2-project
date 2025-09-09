{{ config(materialized='table') }}

SELECT DISTINCT
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state,
    g.geolocation_zip_code_prefix,  
    g.latitude,
    g.longitude,
    current_timestamp AS record_loaded_at
FROM {{ ref('stg_sellers') }} s
LEFT JOIN {{ ref('dim_geolocation') }} g
  ON s.seller_zip_code_prefix = g.geolocation_zip_code_prefix