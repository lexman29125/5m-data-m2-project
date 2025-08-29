{{ config(materialized='view') }}

select
    order_id,
    payment_sequential,
    trim(lower(payment_type)) as payment_type,
    safe_cast(payment_installments as int) as payment_installments,
    safe_cast(payment_value as numeric) as payment_value
from {{ source('raw', 'order_payment') }}