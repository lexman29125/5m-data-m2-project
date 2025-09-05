{{ config(materialized='table') }}

with payment_types as (
select distinct
    {{ dbt_utils.generate_surrogate_key(['payment_type']) }} as payment_type_key,
    payment_type,
    case 
        when payment_type = 'credit_card' then 'Credit Card'
        when payment_type = 'debit_card' then 'Debit Card'
        when payment_type = 'boleto' then 'Boleto Bancário'
        when payment_type = 'voucher' then 'Voucher'
        when payment_type = 'not_defined' then 'Not Defined'
    end as payment_description,
    case 
        when payment_type in ('credit_card', 'debit_card') then 'Card Payment'
        when payment_type = 'boleto' then 'Bank Slip'
        when payment_type = 'voucher' then 'Prepaid Credit'
        when payment_type = 'not_defined' then 'Unknown'
    end as payment_category,
    current_timestamp() as loaded_at
from {{ ref('stg_order_payments') }}
where payment_type is not null

UNION ALL
    
    -- Add the default '-1' key for missing payment types
    select 
        '-1' as payment_type_key,
        'not_defined' as payment_type,
        'Not Defined' as payment_description,
        'Unknown' as payment_category,
        current_timestamp() as loaded_at
)

select * from payment_types
