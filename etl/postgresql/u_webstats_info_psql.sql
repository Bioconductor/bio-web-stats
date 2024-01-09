-- update "Valid through" date

INSERT INTO webstats_info (key, value)
VALUES ('ValidThru', (SELECT MAX(date) FROM bioc_web_downloads))
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value;
