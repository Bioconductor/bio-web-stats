"""Ingest download logs from Athena."""

from datetime import date, timedelta
import pandas as pd
import awswrangler as wr
from flask import current_app
import logging

import bioc_webstats.models as db

def ingest_logs():
    """See https://aws-sdk-pandas.readthedocs.io/en/latest/index.html"""

    
    # current_app.logger.log(logging.INFO, 'Starting ingest')
    # source_connection_string = "s3://bioc-webstats-download-logs/data/year=2024/month=01/day=10/"  # TODO current_app.config["SOURCE LOCATION"]
    # df = wr.s3.read_parquet(source_connection_string, dataset=True)
    # Access to model data
    start_date = db.WebstatsInfo.get_valid_thru_date()
    query_str = f"""
    WITH
  T AS (
   SELECT
     "date"
   , request_ip "c-ip"
   , "status" "sc-status"
   , replace(regexp_extract("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\\.(?:tar|gz|zip|tgz)$', 1), 'data/', '') category
   , regexp_extract("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\\.(?:tar|gz|zip|tgz)$', 2) package
   , LPAD(CAST(year("date") AS VARCHAR), 4, '0') "year"
   , LPAD(CAST(month("date") AS VARCHAR), 2, '0') "month"
   , LPAD(CAST(day("date") AS VARCHAR), 2, '0') "day"
   FROM
     "cloudfront_logs"
   WHERE
    "date" > DATE '{start_date}' AND
    "status" in (200, 301, 302, 307, 308) AND 
    regexp_like("uri", '^/+packages/+[^/]*/+(bioc|workflows|data/+experiment|data/+annotation)/+(?:bin|src)/+(?:[^/]*/+)*([^_]*)_.*\\.(?:tar|gz|zip|tgz)$'))
    SELECT * FROM T WHERE (package <> '')
    LIMIT 10;
"""
    database = "glue-sup-db"
    output = "s3://perf-anal-2022-12-06-rds/"
    result = wr.athena.read_sql_query(sql=query_str, database=database, ctas_approach=True)
    # TODO do I need to move it to parquet first?
    pass
    # foo = df.to_sql('bioc_web_downloads', engine)
    pass

