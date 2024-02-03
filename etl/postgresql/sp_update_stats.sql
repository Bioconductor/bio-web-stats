-- PROCEDURE: public.sp_update_stats()

-- DROP PROCEDURE IF EXISTS public.sp_update_stats();

CREATE OR REPLACE PROCEDURE public.sp_update_stats(
	)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    start_date DATE;
    end_date DATE;
BEGIN
    SELECT TO_DATE(value, 'YYYY-MM-DD') INTO start_date
    FROM webstats_info
    WHERE key = 'ValidThru';
    RAISE NOTICE 'Start Date %', start_date;

	 INSERT INTO stats (category, package, date, is_monthly, ip_count, download_count)
		select category, package, date, is_monthly, ip_count, download_count
			from f_stats(start_date, false, true)
		union all
			select category, package, date, is_monthly, ip_count, download_count
			from f_stats(start_date, true, true)
		ON CONFLICT (package, "date")
		DO UPDATE SET
		category  = EXCLUDED.category,
		"package" = EXCLUDED."package", 
		"date" = EXCLUDED."date",
		is_monthly = EXCLUDED.is_monthly, 
		ip_count = EXCLUDED.ip_count, 
		download_count = EXCLUDED.download_count;
		

	 INSERT INTO categorystats (category, date, is_monthly, ip_count, download_count)
		select category, date, is_monthly, ip_count, download_count
			from f_stats(start_date, false, true)
		union all
			select category, date, is_monthly, ip_count, download_count
			from f_stats(start_date, true, true)
		ON CONFLICT (category, "date")
		DO UPDATE SET
		category  = EXCLUDED.category,
		"date" = EXCLUDED."date",
		is_monthly = EXCLUDED.is_monthly, 
		ip_count = EXCLUDED.ip_count, 
		download_count = EXCLUDED.download_count;

    DELETE FROM stats WHERE date >= start_date;

    INSERT INTO stats
    SELECT * FROM v_stats WHERE date >= start_date;

    DELETE FROM categorystats WHERE date >= start_date;

    INSERT INTO categorystats
    SELECT * FROM v_categorystats WHERE date >= start_date;

    SELECT MAX(date) INTO end_date FROM bioc_web_downloads;

    UPDATE webstats_info
    SET value = end_date
    WHERE key = 'ValidThru';
    RAISE NOTICE 'Update completed through %', end_date;
	
END;
$BODY$;
ALTER PROCEDURE public.sp_update_stats()
    OWNER TO postgres;
