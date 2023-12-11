CREATE UNIQUE INDEX stats_idx_category
    ON public.stats USING btree
    (category ASC NULLS LAST, "package" ASC NULLS LAST, date ASC NULLS LAST, is_monthly ASC NULLS LAST)
    WITH (deduplicate_items=True)
    TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.stats
    CLUSTER ON stats_idx_category;
    