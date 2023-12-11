-- Table: public.stats

-- DROP TABLE IF EXISTS public.stats;

CREATE TABLE IF NOT EXISTS public.stats
(
    category character varying(16) COLLATE pg_catalog."default",
    "package" character varying(64) COLLATE pg_catalog."default",
    date date,
    is_monthly boolean,
    ip_count integer,
    download_count integer
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.stats
    OWNER to postgres;
-- Index: stats_idx_category

-- DROP INDEX IF EXISTS public.stats_idx_category;

CREATE UNIQUE INDEX IF NOT EXISTS stats_idx_category
    ON public.stats USING btree
    (category COLLATE pg_catalog."default" ASC NULLS LAST, package COLLATE pg_catalog."default" ASC NULLS LAST, date ASC NULLS LAST, is_monthly ASC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.stats
    CLUSTER ON stats_idx_category;