{{ config(materialized='incremental', unique_key='order_item_id') }}

with base as (
    select
        oi.order_id,
        oi.order_item_id,
        oi.product_id,
        oi.seller_id,
        o.customer_id,
        CAST(FORMAT_DATE('%Y%m%d', CAST(o.order_purchase_timestamp AS DATE)) AS INT64) AS order_date_key,
        COALESCE(op.payment_type, 'UNKNOWN') AS payment_type_key,
        oi.price,
        oi.freight_value,
        r.review_score,
        DATE_DIFF(CAST(o.order_delivered_customer_date AS DATE), CAST(o.order_purchase_timestamp AS DATE), DAY) AS delivery_time_days
    from {{ ref('stg_order_items') }} oi
    join {{ ref('stg_orders') }} o on oi.order_id = o.order_id
    left join (
        select order_id, MIN(payment_type) as payment_type
        from {{ ref('stg_order_payments') }}
        group by order_id
    ) op on oi.order_id = op.order_id
    left join (
        select order_id, MAX(review_score) as review_score
        from {{ ref('stg_order_reviews') }}
        group by order_id
    ) r on oi.order_id = r.order_id
)

select * except (row_num)
from (
    select
        *,
        row_number() over (partition by order_item_id order by order_id) as row_num
    from base
)
where row_num = 1