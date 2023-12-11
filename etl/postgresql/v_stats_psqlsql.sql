-- View: public.v_stats

-- DROP VIEW public.v_stats;

CREATE OR REPLACE VIEW public.v_stats
 AS
 WITH t AS (
         SELECT UPPER(bioc_web_downloads.category)::varchar(16) as category,
            bioc_web_downloads.package,
            date_trunc('year'::text, bioc_web_downloads.date::timestamp with time zone) AS yr,
            count(DISTINCT bioc_web_downloads."c-ip") AS ip_count,
            count(*) AS download_count
           FROM bioc_web_downloads
          GROUP BY bioc_web_downloads.category, bioc_web_downloads.package, (date_trunc('year'::text, bioc_web_downloads.date::timestamp with time zone))
        )
 SELECT t.category,
    t.package,
    t.yr + '1 year'::interval - '1 day'::interval AS date,
    false AS is_monthly,
    t.ip_count,
    t.download_count
   FROM t
UNION ALL
 SELECT bioc_web_downloads.category,
    bioc_web_downloads.package,
    date_trunc('MONTH'::text, bioc_web_downloads.date::timestamp with time zone) AS date,
    true AS is_monthly,
    count(DISTINCT bioc_web_downloads."c-ip") AS ip_count,
    count(*) AS download_count
   FROM bioc_web_downloads
  GROUP BY bioc_web_downloads.category, bioc_web_downloads.package, (date_trunc('MONTH'::text, bioc_web_downloads.date::timestamp with time zone));

ALTER TABLE public.v_stats
    OWNER TO postgres;

