-- View: public.v_stats

-- DROP VIEW public.v_stats;

CREATE OR REPLACE VIEW public.v_stats
 AS
 WITH t AS (
         SELECT D.category,
            D.package,
            date_trunc('year'::text, D.date::timestamp) AS yr,
            count(DISTINCT D."c-ip") AS ip_count,
            count(*) AS download_count
           FROM bioc_web_downloads as D
           INNER JOIN packages as P 
            ON D.package = P.package and D.category = P.category
            where "sc-status" in (200, 301, 302, 307, 308)
          GROUP BY D.category, D.package, (date_trunc('year'::text, D.date::timestamp))
        )
 SELECT t.category,
    t.package,
    t.yr + '1 year'::interval - '1 day'::interval AS date,
    false AS is_monthly,
    t.ip_count,
    t.download_count
   FROM t
UNION ALL
        SELECT D.category,
            D.package,
    date_trunc('MONTH'::text, D.date::timestamp) AS date,
    true AS is_monthly,
    count(DISTINCT D."c-ip") AS ip_count,
    count(*) AS download_count
           FROM bioc_web_downloads as D
           INNER JOIN packages as P 
            ON D.package = P.package and D.category = P.category
            where "sc-status" in (200, 301, 302, 307, 308)
  GROUP BY D.category, D.package, (date_trunc('MONTH'::text, D.date::timestamp));

ALTER TABLE public.v_stats
    OWNER TO postgres;

