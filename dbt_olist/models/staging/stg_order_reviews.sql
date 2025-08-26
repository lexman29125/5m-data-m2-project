{{ config(materialized='view') }}

select
    review_id,
    order_id,
    review_score,
    cast(review_creation_date as timestamp) as review_creation_date,
    cast(review_answer_timestamp as timestamp) as review_answer_timestamp
from {{ source('raw', 'order_review') }}