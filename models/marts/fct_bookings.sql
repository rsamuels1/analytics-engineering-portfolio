with bookings as (

    select *
    from {{ ref('stg_bookings') }}

),

final as (

    select
        booking_id,
        customer_id,
        booking_date,
        tour_name,
        guest_count,
        booking_status,
        booking_amount,

        case
            when booking_status = 'completed'
            then booking_amount
            else 0
        end as realized_revenue,

        case
            when booking_status = 'confirmed'
            then booking_amount
            else 0
        end as pending_booking_value,

        case
            when booking_status = 'completed' then 1
            else 0
        end as is_completed,

        case
            when booking_status = 'confirmed' then 1
            else 0
        end as is_confirmed,

        case
            when booking_status = 'cancelled' then 1
            else 0
        end as is_cancelled

    from bookings

)

select *
from final