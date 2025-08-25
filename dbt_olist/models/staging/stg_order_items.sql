with source as (
    select * from {{ source('raw', 'order_item') }}
)
select
    order_id,
    order_item_id,
    product_id,
    seller_id,
    price,
    freight_value
from source