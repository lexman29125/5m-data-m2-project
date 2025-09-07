{{ config(materialized='view') }}

WITH ranked AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY customer_id) AS rn
    FROM {{ source('raw', 'customer') }}
)
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    UPPER(customer_state) AS customer_state,
    CURRENT_TIMESTAMP AS record_loaded_at
FROM ranked
WHERE rn = 1