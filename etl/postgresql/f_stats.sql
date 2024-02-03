-- FUNCTION: public.f_stats(date, boolean)
 -- DROP FUNCTION IF EXISTS public.f_stats(date, boolean);

CREATE OR REPLACE FUNCTION PUBLIC.F_STATS(START_DATE date, MONTHLY boolean) 
RETURNS TABLE(CATEGORY CHARACTER varying, 
			  PACKAGE CHARACTER varying, 
			  "date" date, 
			  IS_MONTHLY boolean,
			  IP_COUNT bigint, 
			  DOWNLOAD_COUNT bigint
			 ) 
	 LANGUAGE 'plpgsql' 
	 COST 100 
	 VOLATILE PARALLEL UNSAFE 
AS $BODY$
BEGIN
    RETURN QUERY -- Use RETURN QUERY to return a set of rows
    WITH t AS (
        SELECT d.category,
            d.package,
			CASE
				WHEN monthly
				THEN
					date_trunc('year', d.date::timestamp without time zone) + 
						'1 year'::interval - '1 day'::interval
				ELSE
					date_trunc('MONTH'::text, D.date::timestamp)
			END AS dt,
            "c-ip",
            download_count
        FROM bioc_web_downloads d
        JOIN packages p ON d.package::text = p.package::text AND d.category::text = p.category::text
        WHERE d.date > start_date
    )
    SELECT t.category,
        t.package,
		t.dt::date as date,
        monthly as is_monthly,
        COUNT(DISTINCT t."c-ip") ip_count,
        count(*) as download_count
    FROM t
	GROUP BY t.category, t.package, t.dt
;
END;
$BODY$;


ALTER FUNCTION PUBLIC.F_STATS(date, boolean) OWNER TO POSTGRES;


SELECT *
FROM F_STATS('2023-01-01', TRUE) where package = 'affy';