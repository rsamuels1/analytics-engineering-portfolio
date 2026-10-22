with customers as (

    select *
    from {{ ref('stg_customers') }}

),

booking_summary as (

    select
        customer_id,

        count(*) as total_bookings,

        sum(is_completed) as completed_bookings,

        sum(is_cancelled) as cancelled_bookings,

        sum(realized_revenue) as lifetime_revenue

    from {{ ref('fct_bookings') }}

    group by customer_id

),

final as (

    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.signup_date,
        c.acquisition_channel,
        c.customer_city,

        coalesce(b.total_bookings, 0) as total_bookings,

        coalesce(b.completed_bookings, 0) as completed_bookings,

        coalesce(b.cancelled_bookings, 0) as cancelled_bookings,

        coalesce(b.lifetime_revenue, 0) as lifetime_revenue,

        case
            when coalesce(b.completed_bookings, 0) >= 2
            then 1
            else 0
        end as is_repeat_customer,

        case
            when coalesce(b.completed_bookings, 0) >= 2
                then 'Repeat Customer'
            when coalesce(b.completed_bookings, 0) = 1
                then 'First-Time Customer'
            else 'Prospect'
        end as customer_lifecycle_stage

    from customers c

    left join booking_summary b
        on c.customer_id = b.customer_id

)

select *
from final