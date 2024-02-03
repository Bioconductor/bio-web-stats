-- FUNCTION: public.f_stats(date, boolean, boolean)

-- DROP FUNCTION IF EXISTS public.f_stats(date, boolean, boolean);

CREATE OR REPLACE FUNCTION public.f_stats(
	start_date date,
	monthly boolean,
	by_package boolean)
    RETURNS TABLE(category character varying, package character varying, date timestamp without time zone, is_monthly boolean, ip_count bigint, download_count bigint) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
	adjusted_start_date DATE;
BEGIN
	adjusted_start_date := 
		CASE
			WHEN monthly
			THEN
				date_trunc('MONTH'::text, start_date::timestamp without time zone)
			ELSE
				date_trunc('year', start_date::timestamp without time zone)
		END;

    RETURN QUERY -- Use RETURN QUERY to return a set of rows
        SELECT d.category,
			CASE
				WHEN by_package
				THEN d.package
				ELSE '*'
			END as package,
			CASE
				WHEN monthly
				THEN
					date_trunc('MONTH'::text, D.date::timestamp without time zone)
				ELSE
					date_trunc('year', d.date::timestamp without time zone) + 
						'1 year'::interval - '1 day'::interval
			END AS "date",
			MONTHLY as is_monthly,
			COUNT(DISTINCT "c-ip") ip_count,
			count(*) as download_count
        FROM bioc_web_downloads d
        JOIN packages p ON d.package::text = p.package::text AND d.category::text = p.category::text
        WHERE d.date >= adjusted_start_date
		GROUP BY d.category, 
			CASE
				WHEN by_package
				THEN d.package
				ELSE '*'
			END,
			CASE
				WHEN monthly
				THEN
					date_trunc('MONTH'::text, D.date::timestamp without time zone)
				ELSE
					date_trunc('year', d.date::timestamp without time zone) + '1 year'::interval - '1 day'::interval
			END

;
END;
$BODY$;

ALTER FUNCTION public.f_stats(date, boolean, boolean)
    OWNER TO postgres;
