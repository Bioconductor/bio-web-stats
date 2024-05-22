"""Ingest download logs from Athena."""

from datetime import date, timedelta
import pandas as pd
import boto3
import awswrangler as wr
from flask import current_app
import logging


def ingest_logs():
    """See https://aws-sdk-pandas.readthedocs.io/en/latest/index.html"""

    boto3.setup_default_session(profile_name = 'bioc')

    # current_app.logger.log(logging.INFO, 'Starting ingest')
    # source_connection_string = "s3://bioc-webstats-download-logs/data/year=2024/month=01/day=10/"  # TODO current_app.config["SOURCE LOCATION"]
    # df = wr.s3.read_parquet(source_connection_string, dataset=True)
    # Access to model data
    start_date = date(2024, 5, 6)
    end_date = date(2024, 5, 13)
    #modified_date = (start_date + timedelta(days=1))
#    end_date = start_date # should be max date - 1day

    start_date = date.strftime(start_date, "%Y-%m-%d")
    end_date = date.strftime(end_date, "%Y-%m-%d")
    query_str = f"""
    WITH
  T AS (
   SELECT
     "date"
   , request_ip "c-ip"
   , "status" "sc-status"
   , replace(regexp_extract("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$', 1), 'data/', '') category
   FROM
     "cloudfront_logs"
   WHERE
    "status" in (200, 301, 302, 307, 308) AND 
    "date" between DATE '{start_date}' and DATE '{end_date}' AND
    regexp_like("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\.(?:tar|gz|zip|tgz)$'))
) 
SELECT *
FROM
  T
WHERE (package <> '')
"""
    database = "default"
    result = wr.athena.read_sql_query(sql=query_str, database=database, ctas_approach=True)
    
    result.to_csv("~/Downloads/df.csv", index = False)
    # TODO do I need to move it to parquet first?
    pass
    # foo = df.to_sql('bioc_web_downloads', engine)
    pass
# \copy public.bioc_web_downloads (date, "c-ip", "sc-status", category, "package") 
# 	FROM '47451b6a-96d7-4003-844d-56875d89b53c.csv'
# DELIMITER ',' CSV HEADER ENCODING 'UTF8' QUOTE '"' ESCAPE '''';

# CHECK THE COUNTS

#####################
# BEGIN; -- Start a transaction

# DELETE FROM stats WHERE "date" >= date '2024-03-01';

# INSERT INTO stats
# SELECT * FROM v_stats WHERE "date" >= date '2024-03-01';

# DELETE FROM categorystats WHERE "date" >= date '2024-03-01';

# INSERT INTO categorystats
# SELECT * FROM v_categorystats WHERE "date" >= date '2024-03-01';

# update webstats_info 
#         set value = (select max(date) from bioc_web_downloads)
#         where key = 'ValidThru';
        
# COMMIT;

# -- If there are any issues, you can rollback the transaction
# -- ROLLBACK;

#####################

# REPORT THE UPDATE

# aws cloudfront create-invalidation --distribution-id E1TVLJONPTUXV3 --paths '/packages/stats/*'

# REPORT THE INVALIDATION
ingest_logs()
