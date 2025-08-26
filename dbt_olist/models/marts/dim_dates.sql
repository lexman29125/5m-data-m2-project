{{ config(materialized='table') }}

with dates as (
    select distinct cast(order_purchase_timestamp as date) as full_date
    from {{ ref('stg_orders') }}
)
select
    cast(format_date('%Y%m%d', full_date) as int64) as date_key,
    full_date,
    format_date('%A', full_date) as day_of_week,
    format_date('%B', full_date) as month_name,
    extract(year from full_date) as year,
    extract(quarter from full_date) as quarter
from dates