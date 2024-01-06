insert into stats
with T as (select category,
    package,
    year(D."date") "yr",
    count(distinct D."c-ip") ip_count,
    count(*) download_count
    FROM bioc_web_downloads as D
    INNER JOIN packages as P 
    ON D.package = P.package and D.category = P.category
    group by D.category,
        D.package,
        year(D."date")
)
select "category", "package", 
    CAST(CAST(yr AS VARCHAR) || '-12-31' AS DATE) "date", 
    false as is_monthly,
    "ip_count", 
    "download_count" 
from T
UNION ALL
select D.category,
    D.package,
    date_trunc('MONTH', D."date") "date", 
    true as is_monthly,
    count(distinct D."c-ip") ip_count,
    count(*) download_count
    FROM bioc_web_downloads as D
    INNER JOIN packages as P 
    ON D.package = P.package and D.category = P.category
group by category,
    D.package,
    date_trunc('MONTH', D."date")
