-- View: public.v_categorystats

-- DROP VIEW public.v_categorystats;

CREATE OR REPLACE VIEW public.v_categorystats
 AS

WITH s AS (
	SELECT * 
		FROM bioc_web_downloads
		WHERE LOWER(package) in (select lower_package from packages)
	),
t AS (
         SELECT category,
            date_trunc('year', "date") AS yr,
            count(DISTINCT "c-ip") AS ip_count,
            count(*) AS download_count
           FROM s
          GROUP BY category, date_trunc('year', "date")
 )
 SELECT t.category,
    t.yr + '1 year'::interval - '1 day'::interval AS date,
    false AS is_monthly,
    t.ip_count,
    t.download_count
   FROM t
UNION ALL
 SELECT category,
    date_trunc('MONTH', date) AS date,
    true AS is_monthly,
    count(DISTINCT "c-ip") AS ip_count,
    count(*) AS download_count
   FROM s
  GROUP BY category, (date_trunc('MONTH', "date"))

ALTER TABLE public.v_categorystats
    OWNER TO postgres;

