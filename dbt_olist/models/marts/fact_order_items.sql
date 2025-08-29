{{ config(
    materialized='incremental',
    unique_key='order_item_id'
) }}

with order_payments as (
    select
        order_id,
        {{ dbt_utils.generate_surrogate_key(['payment_type']) }} as payment_type_key
    from (
        select
            order_id,
            lower(payment_type) as payment_type,
            row_number() over(
                partition by order_id 
                order by 
                    case payment_type                   -- Select a single, prioritized payment type for each order.
                        when 'credit_card' then 1       -- Highest Priority
                        when 'debit_card' then 2
                        when 'boleto' then 3
                        when 'voucher' then 4
                        else 5
                    end,
                    payment_type
            ) as rn
        from {{ ref('stg_order_payments') }}
        where payment_type is not null
    )
    where rn = 1
),

order_reviews as (
    select
        order_id,
        max(review_score) as review_score
    from {{ ref('stg_order_reviews') }}
    where review_score is not null
    group by order_id
),

base_data as (
    select
        oi.order_id,
        oi.order_item_id,
        oi.product_id,
        oi.seller_id,
        o.customer_id,
        cast(format_date('%Y%m%d', date(o.order_purchase_timestamp)) as int64) as order_date_key,
        coalesce(op.payment_type_key, '-1') as payment_type_key,
        oi.price,
        oi.freight_value,
        r.review_score,  
        date_diff(date(o.order_delivered_customer_date), date(o.order_purchase_timestamp), day) as delivery_time_days,
        o.order_purchase_timestamp
    from {{ ref('stg_order_items') }} oi
    inner join {{ ref('stg_orders') }} o
        on oi.order_id = o.order_id
    left join order_payments op
        on oi.order_id = op.order_id
    left join order_reviews r
        on oi.order_id = r.order_id
    where o.order_purchase_timestamp is not null

    {% if is_incremental() %}
        -- Filters for new records since the last run
        and o.order_purchase_timestamp > (
            select coalesce(max(order_purchase_timestamp), timestamp('1900-01-01'))
            from {{ this }}
        )
    {% endif %}
),

final as (
    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        customer_id,
        order_date_key,
        payment_type_key,
        price,
        freight_value,
        review_score,
        delivery_time_days
    from (
        select
            *,
            row_number() over (
                partition by order_item_id 
                order by order_purchase_timestamp desc
            ) as rn
        from base_data
    )
    where rn = 1
)

select 
    *,
    current_timestamp as loaded_at
from final
