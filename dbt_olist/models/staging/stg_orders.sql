{{ config(materialized='view') }}

select
    order_id,
    customer_id,
    lower(order_status) as order_status,
    safe_cast(nullif(order_purchase_timestamp, '') as timestamp) as order_purchase_timestamp,
    safe_cast(nullif(order_approved_at, '') as timestamp) as order_approved_at,
    safe_cast(nullif(order_delivered_carrier_date, '') as timestamp) as order_delivered_carrier_date,
    safe_cast(nullif(order_delivered_customer_date, '') as timestamp) as order_delivered_customer_date,
    safe_cast(nullif(order_estimated_delivery_date, '') as timestamp) as order_estimated_delivery_date,
    current_timestamp as record_loaded_at
from {{ source('raw', 'order') }}