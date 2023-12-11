-- Table: public.bioc_web_downloads

-- DROP TABLE IF EXISTS public.bioc_web_downloads;

CREATE TABLE IF NOT EXISTS public.bioc_web_downloads
(
    date date,
    "c-ip" character varying(40) COLLATE pg_catalog."default",
    "sc-status" integer,
    category character varying(16) COLLATE pg_catalog."default",
    "package" character varying(64) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.bioc_web_downloads
    OWNER to postgres;
-- Index: idx_date

-- DROP INDEX IF EXISTS public.idx_date;

CREATE INDEX IF NOT EXISTS idx_date
    ON public.bioc_web_downloads USING btree
    (date ASC NULLS LAST, "c-ip" COLLATE pg_catalog."default" ASC NULLS LAST, category COLLATE pg_catalog."default" ASC NULLS LAST, package COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.bioc_web_downloads
    CLUSTER ON idx_date;