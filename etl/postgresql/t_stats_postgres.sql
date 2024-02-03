-- Table: public.stats

-- DROP TABLE IF EXISTS public.stats;

CREATE TABLE IF NOT EXISTS public.stats
(
    category character varying(16) COLLATE pg_catalog."default",
    "package" character varying(64) COLLATE pg_catalog."default" NOT NULL,
    "date" date NOT NULL,
    is_monthly boolean NOT NULL,
    ip_count integer,
    download_count integer,
    CONSTRAINT stats_pkey PRIMARY KEY ("package", "date")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.stats
    OWNER to postgres;