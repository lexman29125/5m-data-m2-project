with source as (
    select * from {{ source('raw', 'customer') }}
)
select
    customer_id,
    customer_unique_id,
    customer_city,
    customer_state,
    customer_zip_code_prefix -- NEW: used for geolocation enrich
from source