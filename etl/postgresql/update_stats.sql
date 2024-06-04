-- PROCEDURE: public.update_stats(date)

-- DROP PROCEDURE IF EXISTS public.update_stats(date);

CREATE OR REPLACE PROCEDURE public.update_stats(
	IN p_date date)
LANGUAGE 'plpgsql'
AS $BODY$
BEGIN
    DELETE FROM stats WHERE "date" >= p_date;
    INSERT INTO stats
    SELECT * FROM v_stats WHERE "date" >= p_date;

    DELETE FROM categorystats WHERE "date" >= p_date;
    INSERT INTO categorystats
    SELECT * FROM v_categorystats WHERE "date" >= p_date;

    UPDATE webstats_info 
    SET value = (SELECT MAX(date) FROM bioc_web_downloads)
    WHERE key = 'ValidThru';
END;
$BODY$;
ALTER PROCEDURE public.update_stats(date)
    OWNER TO postgres;
