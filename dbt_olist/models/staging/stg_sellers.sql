{{ config(materialized='view') }}

WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY seller_id ORDER BY seller_id) AS rn
    FROM {{ source('raw', 'seller') }}
)
SELECT
    seller_id,
    seller_zip_code_prefix,
    TRIM(LOWER(seller_city)) AS seller_city,
    TRIM(UPPER(seller_state)) AS seller_state,
    CURRENT_TIMESTAMP AS record_loaded_at
FROM ranked
WHERE rn = 1