{{ config(materialized='view') }}

select
    product_id,
    trim(product_category_name) as product_category_name,
    safe_cast(product_weight_g as numeric) as product_weight_g,
    safe_cast(product_length_cm as numeric) as product_length_cm,
    safe_cast(product_height_cm as numeric) as product_height_cm,
    safe_cast(product_width_cm as numeric) as product_width_cm,
    current_timestamp as record_loaded_at
from {{ source('raw', 'product') }} 
