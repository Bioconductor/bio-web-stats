insert into categorystats
with T as (select category,
    year("date") "yr",
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    year("date")
)
select "category", 
    CAST(CAST(yr AS VARCHAR) || '-12-31' AS DATE) "date", 
    false as is_monthly,
    "ip_count", 
    "download_count" 
from T
UNION ALL
select category,
    date_trunc('MONTH', "date") "date", 
    true as is_monthly,
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    date_trunc('MONTH', "date")
