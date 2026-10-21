with source as (

    select *
    from {{ source('raw', 'bookings') }}

),

renamed as (

    select
        booking_id,
        customer_id,
        to_date(booking_date) as booking_date,
        tour_name,
        guests as guest_count,
        total_amount as booking_amount,
        lower(trim(status)) as booking_status

    from source

)

select *
from renamed