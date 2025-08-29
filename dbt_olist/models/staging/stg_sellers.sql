{{ config(materialized='view') }}

select
    seller_id,
    seller_zip_code_prefix,
    trim(lower(seller_city)) as seller_city,
    trim(upper(seller_state)) as seller_state,
    current_timestamp as record_loaded_at
from {{ source('raw', 'seller') }}