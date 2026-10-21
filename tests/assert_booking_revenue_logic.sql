select
    booking_id,
    booking_status,
    booking_amount,
    realized_revenue,
    pending_booking_value

from {{ ref('fct_bookings') }}

where
    realized_revenue != case
        when booking_status = 'completed'
        then booking_amount
        else 0
    end

    or

    pending_booking_value != case
        when booking_status = 'confirmed'
        then booking_amount
        else 0
    end