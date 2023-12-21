-- View: public.categorystats

-- DROP MATERIALIZED VIEW IF EXISTS public.categorystats;

CREATE MATERIALIZED VIEW IF NOT EXISTS public.categorystats
TABLESPACE pg_default
AS
 WITH s AS (
         SELECT bioc_web_downloads.date,
            bioc_web_downloads."c-ip",
            bioc_web_downloads."sc-status",
            bioc_web_downloads.category,
            bioc_web_downloads.package
           FROM bioc_web_downloads
          WHERE (lower(bioc_web_downloads.package::text) IN ( SELECT packages.lower_package
                   FROM packages))
        ), t AS (
         SELECT s.category,
            date_trunc('year'::text, s.date::timestamp with time zone) AS yr,
            count(DISTINCT s."c-ip") AS ip_count,
            count(*) AS download_count
           FROM s
          GROUP BY s.category, (date_trunc('year'::text, s.date::timestamp with time zone))
        )
 SELECT t.category,
    t.yr + '1 year'::interval - '1 day'::interval AS date,
    false AS is_monthly,
    t.ip_count,
    t.download_count
   FROM t
UNION ALL
 SELECT s.category,
    date_trunc('MONTH'::text, s.date::timestamp with time zone) AS date,
    true AS is_monthly,
    count(DISTINCT s."c-ip") AS ip_count,
    count(*) AS download_count
   FROM s
  GROUP BY s.category, (date_trunc('MONTH'::text, s.date::timestamp with time zone))
WITH NO DATA;

ALTER TABLE IF EXISTS public.categorystats
    OWNER TO postgres;


CREATE INDEX categorystats_idx_category_date
    ON public.categorystats USING btree
    (category COLLATE pg_catalog."default", date)
    TABLESPACE pg_default;