with campaign_performance as (

    select
        performance_date,
        campaign_id,
        campaign_name,
        channel,
        campaign_type,
        impressions,
        clicks,
        spend,
        conversions,
        revenue,

        clicks / nullif(impressions, 0) as ctr,
        spend / nullif(clicks, 0) as cpc,
        spend / nullif(conversions, 0) as cpa,
        revenue / nullif(spend, 0) as roas

    from {{ ref('stg_google_ads') }}

)

select *
from campaign_performance
