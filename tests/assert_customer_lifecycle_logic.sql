select
    customer_id,
    completed_bookings,
    is_repeat_customer,
    customer_lifecycle_stage

from {{ ref('dim_customer') }}

where
    customer_lifecycle_stage != case
        when completed_bookings >= 2 then 'Repeat Customer'
        when completed_bookings = 1 then 'First-Time Customer'
        else 'Prospect'
    end

    or

    is_repeat_customer != case
        when completed_bookings >= 2 then 1
        else 0
    end