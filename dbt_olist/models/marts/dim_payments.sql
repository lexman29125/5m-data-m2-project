{{ config(materialized='table') }}

select distinct
    payment_type as payment_type_key,
    payment_type
from {{ ref('stg_order_payments') }} p
