{{ config(materialized='view') }}

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    upper(customer_state) as customer_state,
    current_timestamp as record_loaded_at
from {{ source('raw', 'customer') }}