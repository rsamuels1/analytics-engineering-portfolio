select
    performance_date,
    campaign_id,
    count(*) as row_count
from {{ ref('fct_campaign_performance') }}
group by
    performance_date,
    campaign_id
having count(*) > 1
