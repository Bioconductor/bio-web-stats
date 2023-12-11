create view v_stats as
with T as (select category,
    package,
    DATE_TRUNC('year', "date") "yr",
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    package,
    DATE_TRUNC('year', "date")
)
select "category", "package", 
    yr + INTERVAL '1 year' - INTERVAL '1 day' AS "date",
    cast('false' as BOOLEAN) as is_monthly,
    "ip_count", 
    "download_count" 
from T
UNION ALL
select category,
    package,
    date_trunc('MONTH', "date") "date", 
    cast('true' as BOOLEAN) as is_monthly,
    count(distinct "c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    package,
    date_trunc('MONTH', "date")
