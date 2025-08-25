-- Geolocation has multiple rows per zip prefix; standardize to one row per prefix
with source as (
    select * from {{ source('raw', 'geolocation') }}
),
ranked as (
    select
        geolocation_zip_code_prefix as zip_prefix,
        geolocation_city as city,
        geolocation_state as state,
        avg(cast(geolocation_lat as float64)) as lat,
        avg(cast(geolocation_lng as float64)) as lng,
        count(*) as cnt,
        row_number() over (
            partition by geolocation_zip_code_prefix
            order by count(*) desc, geolocation_city asc, geolocation_state asc
        ) as rn
    from source
    group by 1,2,3
)
select
    zip_prefix,
    city,
    state,
    lat,
    lng
from ranked
where rn = 1