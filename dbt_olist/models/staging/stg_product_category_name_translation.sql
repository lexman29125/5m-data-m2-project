{{ config(materialized='view') }}

select
    trim(product_category_name) as product_category_name,
    trim(product_category_name_english) as product_category_name_english,
    current_timestamp as record_loaded_at
from {{ source('raw', 'product_category_name_translation') }}