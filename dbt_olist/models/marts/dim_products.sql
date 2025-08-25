{{ config(materialized='table') }}

select
    p.product_id,
    t.product_category_name_english,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from {{ ref('stg_products') }} p
left join {{ ref('product_category_name_translation') }} t
    on p.product_category_name = t.product_category_name