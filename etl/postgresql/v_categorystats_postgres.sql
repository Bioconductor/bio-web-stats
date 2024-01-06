-- View: public.categorystats

-- DROP MATERIALIZED VIEW IF EXISTS public.categorystats;

CREATE MATERIALIZED VIEW IF NOT EXISTS public.categorystats
TABLESPACE pg_default
AS
 WITH s AS (
         SELECT D.date,
            D."c-ip",
            D."sc-status",
            D.category,
            D.package
           FROM bioc_web_downloads as D
           INNER JOIN packages P 
            ON D.package = P.package AND D.category = P.category
 ), t AS (
         SELECT s.category,
            date_trunc('YEAR', s.date) AS yr,
            count(DISTINCT s."c-ip") AS ip_count,
            count(*) AS download_count
           FROM s
          GROUP BY s.category, date_trunc('YEAR', s.date)
        )
 SELECT t.category,
    (t.yr + '1 YEAR'::interval - '1 day'::interval)::date AS date,
    false AS is_monthly,
    t.ip_count,
    t.download_count
   FROM t
UNION ALL
 SELECT s.category,
    date_trunc('MONTH', s.date)::date AS date,
    true AS is_monthly,
    count(DISTINCT s."c-ip") AS ip_count,
    count(*) AS download_count
   FROM s
  GROUP BY s.category, (date_trunc('MONTH', s.date))
WITH NO DATA;

ALTER TABLE IF EXISTS public.categorystats
    OWNER TO postgres;


CREATE INDEX categorystats_idx_category_date
    ON public.categorystats USING btree
    (category COLLATE pg_catalog."default", date)
    TABLESPACE pg_default;