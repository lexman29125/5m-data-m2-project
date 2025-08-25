with source as (
    select * from {{ source('raw', 'order_payment') }}
)
select
    order_id,
    payment_type,
    payment_value
from source