with source as (

    select *
    from {{ source('raw', 'customers') }}

),

renamed as (

    select
        customer_id,
        first_name,
        last_name,
        lower(trim(email)) as email,
        to_date(signup_date) as signup_date,

        coalesce(
            nullif(trim(acquisition_channel), ''),
            'Unknown'
        ) as acquisition_channel,

        customer_city

    from source

)

select *
from renamed