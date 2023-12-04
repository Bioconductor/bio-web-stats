select strftime(
        '%Y-%m-%d',
        substr(day_month_year, 8, 4) || '-' || case
            substr(day_month_year, 4, 3)
            when 'Jan' then '01'
            when 'Feb' then '02'
            when 'Mar' then '03'
            when 'Apr' then '04'
            when 'May' then '05'
            when 'Jun' then '06'
            when 'Jul' then '07'
            when 'Aug' then '08'
            when 'Sep' then '09'
            when 'Oct' then '10'
            when 'Nov' then '11'
            when 'Dec' then '12'
        end || '-' || substr(day_month_year, 1, 2)
    ) AS "date",
    ips as "c-ip",
    statuscode as "sc-status",
    "url" as "cs-uri-stem"
from access_log
