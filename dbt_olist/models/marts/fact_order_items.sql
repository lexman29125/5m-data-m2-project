{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

with oi as (
    select * from {{ ref('stg_order_items') }}
),
o as (
    select
        order_id,
        customer_id,
        cast(order_purchase_timestamp as date) as order_date,
        cast(order_delivered_customer_date as date) as delivered_date
    from {{ ref('stg_orders') }}
),
p as (
    select * from {{ ref('stg_order_payments') }}
),
r as (
    select * from {{ ref('stg_order_reviews') }}
)

select
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    cast(format_date('%Y%m%d', o.order_date) as int) as order_date_key,
    p.payment_type as payment_type_key,
    oi.price,
    oi.freight_value,
    r.review_score,
    date_diff(o.delivered_date, o.order_date, day) as delivery_time_days
from oi
join o on oi.order_id = o.order_id
left join p on oi.order_id = p.order_id
left join r on oi.order_id = r.order_id

{% if is_incremental() %}
  where o.order_date > (select max(full_date) from {{ ref('dim_dates') }})
{% endif %}