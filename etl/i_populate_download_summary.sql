insert into stats
with T as (select category,
    package,
    year("date") "yr",
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
where lower(package) IN (select lower(package) from packages)
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
    date_trunc('MONTH', "date") "date", 
    true as is_monthly,
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    package,
    date_trunc('MONTH', "date")
