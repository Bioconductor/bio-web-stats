-- Table: public.packages

-- DROP TABLE IF EXISTS public.packages;

CREATE TABLE IF NOT EXISTS public.packages
(
    category character varying(16) COLLATE pg_catalog."default" NOT NULL,
    "package" character varying(64) COLLATE pg_catalog."default" NOT NULL,
    first_version character varying(8) COLLATE pg_catalog."default" NOT NULL,
    last_version character varying(8) COLLATE pg_catalog."default",
    lower_package character varying(64) COLLATE pg_catalog."default" NOT NULL GENERATED ALWAYS AS (lower((package)::text)) STORED,
    CONSTRAINT packages_pkey PRIMARY KEY (category, "package")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.packages
    OWNER to postgres;
-- Index: packages_idx_lower_names

-- DROP INDEX IF EXISTS public.packages_idx_lower_names;

CREATE UNIQUE INDEX IF NOT EXISTS packages_idx_lower_names
    ON public.packages USING btree
    (lower_package COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (deduplicate_items=False)
    TABLESPACE pg_default;
-- Index: packages_idx_package

-- DROP INDEX IF EXISTS public.packages_idx_package;

CREATE UNIQUE INDEX IF NOT EXISTS packages_idx_package
    ON public.packages USING btree
    (package COLLATE pg_catalog."default" ASC NULLS LAST)
    WITH (deduplicate_items=False)
    TABLESPACE pg_default;