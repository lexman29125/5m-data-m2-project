with source as (
    select * from {{ source('raw', 'seller') }}
)
select
    seller_id,
    seller_city,
    seller_state,
    seller_zip_code_prefix -- NEW: used for geolocation enrich
from source