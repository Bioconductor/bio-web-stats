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

GRANT ALL ON TABLE public.bioc_web_downloads TO postgres;

GRANT ALL ON TABLE public.bioc_web_downloads TO webstats_runner;
-- Index: idx_bioc_web_downloads_category_package

-- DROP INDEX IF EXISTS public.idx_bioc_web_downloads_category_package;

CREATE INDEX IF NOT EXISTS idx_bioc_web_downloads_category_package
    ON public.bioc_web_downloads USING btree
    (category COLLATE pg_catalog."default" ASC NULLS LAST, package COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_bioc_web_downloads_cip

-- DROP INDEX IF EXISTS public.idx_bioc_web_downloads_cip;

CREATE INDEX IF NOT EXISTS idx_bioc_web_downloads_cip
    ON public.bioc_web_downloads USING btree
    ("c-ip" COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_bioc_web_downloads_date

-- DROP INDEX IF EXISTS public.idx_bioc_web_downloads_date;

CREATE INDEX IF NOT EXISTS idx_bioc_web_downloads_date
    ON public.bioc_web_downloads USING btree
    (date ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_bioc_web_downloads_scstatus

-- DROP INDEX IF EXISTS public.idx_bioc_web_downloads_scstatus;

CREATE INDEX IF NOT EXISTS idx_bioc_web_downloads_scstatus
    ON public.bioc_web_downloads USING btree
    ("sc-status" ASC NULLS LAST)
    TABLESPACE pg_default;