with source as (
    select * from {{ source('raw', 'order') }}
)
select
    order_id,
    customer_id,
    cast(order_purchase_timestamp as date) as order_date,
    cast(order_delivered_customer_date as date) as delivered_date,
    cast(order_estimated_delivery_date as date) as estimated_delivery_date   -- NEW
from source