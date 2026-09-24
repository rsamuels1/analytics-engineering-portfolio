select *
from {{ ref('stg_google_ads') }}
where spend < 0
