-- create view v_stats as
with T as (select category,
    package,
    year("date") "yr",
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    package,
    year("date")
)
select "category", "package", 
    CAST(CAST(yr AS VARCHAR) || '-12-31' AS DATE) "date", 
    false as is_monthly,
    "ip_count", 
    "download_count" 
from T
UNION ALL
select category,
    package,
    DATE_TRUNC('year', "date") + INTERVAL '1 year' - INTERVAL '1 day' AS date
    date_trunc('MONTH', "date") "date", 
    true as is_monthly,
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    package,
    date_trunc('MONTH', "date")
