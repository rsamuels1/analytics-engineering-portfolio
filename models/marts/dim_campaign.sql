select distinct
    campaign_id,
    campaign_name,
    channel,
    campaign_type

from {{ ref('stg_google_ads') }}
