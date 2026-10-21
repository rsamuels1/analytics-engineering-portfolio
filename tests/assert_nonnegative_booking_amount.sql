select *
from {{ ref('stg_bookings') }}
where booking_amount < 0