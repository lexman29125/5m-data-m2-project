{{ config(materialized='view') }}

select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    safe_cast(shipping_limit_date as timestamp) as shipping_limit_timestamp,
    safe_cast(price as numeric) as price,
    safe_cast(freight_value as numeric) as freight_value,
    current_timestamp as record_loaded_at
from {{ source('raw', 'order_item') }}