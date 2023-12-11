-- Table: public.webstats_info

-- DROP TABLE IF EXISTS public.webstats_info;

CREATE TABLE IF NOT EXISTS public.webstats_info
(
    key character varying(23) COLLATE pg_catalog."default" NOT NULL,
    value character varying(128) COLLATE pg_catalog."default",
    CONSTRAINT webstats_info_pkey PRIMARY KEY (key)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.webstats_info
    OWNER to postgres;