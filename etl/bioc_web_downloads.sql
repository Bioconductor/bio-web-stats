CREATE OR REPLACE VIEW bioc_web_downloads AS
 with T1 as (
    select "date", "c-ip", "sc-status", "cs-uri-stem", 
    regexp_extract("cs-uri-stem", '^/+packages/(?:[^/]*)/+([^/]*)/+([^/]*)/+(?:[^/]*/)*([^_]*)_.*tar\.(?:gz|zip|tgz)$', 1) path1,
    regexp_extract("cs-uri-stem", '^/+packages/(?:[^/]*)/+([^/]*)/+([^/]*)/+(?:[^/]*/)*([^_]*)_.*tar\.(?:gz|zip|tgz)$', 2) path2,
    regexp_extract("cs-uri-stem", '^/+packages/(?:[^/]*)/+([^/]*)/+([^/]*)/+(?:[^/]*/)*([^_]*)_.*tar\.(?:gz|zip|tgz)$', 3) package
    from "bioc_web_logs"
    where "sc-status" between 200 and 399 and 
    regexp_like("cs-uri-stem", '^/packages/(?:[^/]*)/([^/]*)/([^/]*)/(?:[^/]*/)*([^_]*)_.*tar\.(?:gz|zip|tgz)$')
), 

T2 as (
select "date", "c-ip", "sc-status", "cs-uri-stem", 
    case
        when path1 in ('bioc', 'workflows') then path1
        when path1 = 'data'
            then path2
        else ''
    end "category",
    "package"
from T1)
select year("date") "year", month("date") "month", * from T2 where "category" <> ''
