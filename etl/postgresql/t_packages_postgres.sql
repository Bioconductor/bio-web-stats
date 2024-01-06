-- Table: public.packages

-- DROP TABLE IF EXISTS public.packages;

CREATE TABLE IF NOT EXISTS public.packages
(
    "package" character varying(64) COLLATE pg_catalog."default" NOT NULL,
    category character varying(16) COLLATE pg_catalog."default" NOT NULL,
    first_version character varying(8) COLLATE pg_catalog."default" NOT NULL,
    last_version character varying(8) COLLATE pg_catalog."default",
    CONSTRAINT packages_pkey PRIMARY KEY ("package")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.packages
    OWNER to postgres;
