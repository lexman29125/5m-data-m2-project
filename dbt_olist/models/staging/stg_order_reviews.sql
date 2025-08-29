{{ config(materialized='view') }}

select
    review_id,
    order_id,
    safe_cast(review_score as int) as review_score,
    safe_cast(review_creation_date as timestamp) as review_creation_date,
    safe_cast(review_answer_timestamp as timestamp) as review_answer_timestamp,
    current_timestamp as record_loaded_at  
from {{ source('raw', 'order_review') }}