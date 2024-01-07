-- Table: public.categorystats

-- DROP TABLE IF EXISTS public.categorystats;

CREATE TABLE IF NOT EXISTS public.categorystats
(
    category character varying(16) COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL,
    is_monthly boolean NOT NULL,
    ip_count integer,
    download_count integer,
    CONSTRAINT categorystats_pkey PRIMARY KEY (category, "date", is_monthly)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.categorystats
    OWNER to postgres;
