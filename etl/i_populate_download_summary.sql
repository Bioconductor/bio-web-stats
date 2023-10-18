select category,
    package,
    date_trunc('MONTH', "date") "date",
    count("c-ip") ip_count,
    count(*) download_count
from bioc_web_downloads
group by category,
    package,
    date_trunc('MONTH', "date")