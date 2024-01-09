-- View: public.v_categorystats

CREATE OR REPLACE VIEW public.v_categorystats
AS
 WITH s AS (
         SELECT D.date,
            D."c-ip",
            D."sc-status",
            D.category
           FROM bioc_web_downloads as D
           INNER JOIN packages P 
            ON D.package = P.package AND D.category = P.category
            where "sc-status" in (200, 301, 302, 307, 308)
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
  GROUP BY s.category, (date_trunc('MONTH', s.date));