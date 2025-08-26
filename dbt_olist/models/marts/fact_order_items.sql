{{ config(materialized='incremental', unique_key='order_id') }}

select
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    cast(format_date('%Y%m%d', cast(o.order_purchase_timestamp as date)) as int64) as order_date_key,
    op.payment_type as payment_type_key,
    oi.price,
    oi.freight_value,
    r.review_score,
    date_diff(cast(o.order_delivered_customer_date as date), cast(o.order_purchase_timestamp as date), day) as delivery_time_days
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
left join {{ ref('stg_order_payments') }} op on oi.order_id = op.order_id
left join {{ ref('stg_order_reviews') }} r on oi.order_id = r.order_id