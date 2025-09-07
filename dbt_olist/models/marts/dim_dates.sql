{{ config(materialized='table') }}

with dates as (
    -- Use the same date extraction logic as fact table
    select distinct date(order_purchase_timestamp) as full_date
    from {{ ref('stg_orders') }} o
    where order_purchase_timestamp is not null
      and exists (
          select 1 
          from {{ ref('stg_order_items') }} oi 
          where oi.order_id = o.order_id
      )
)
select
    cast(format_date('%Y%m%d', full_date) as int64) as date_key,
    full_date,
    format_date('%A', full_date) as day_of_week,
    format_date('%B', full_date) as month_name,
    extract(year from full_date) as year,
    extract(quarter from full_date) as quarter,
    current_timestamp as record_loaded_at
from dates