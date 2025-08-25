with source as (
    select * from {{ source('raw', 'order_review') }}
)
select
    order_id,
    review_score
from source