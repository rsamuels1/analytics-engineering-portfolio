with source as (

    select *
    from {{ source('raw', 'google_ads_daily') }}

),

renamed as (

    select
        date as performance_date,
        campaign_id,
        campaign_name,
        channel,
        campaign_type,
        impressions,
        clicks,
        cost as spend,
        conversions,
        conversion_value as revenue

    from source

)

select *
from renamed
