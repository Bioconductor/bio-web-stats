"""Ingest download logs from Athena."""

from typing import Optional
from datetime import date, timedelta, datetime
import pandas as pd
import boto3
import awswrangler as wr
from flask import current_app
import logging

import bioc_webstats.models as db

def ingest_logs(
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    aws_profile: Optional[chr] = "bioc",
    source_database: Optional[chr] = "default",
    result_filename: Optional[chr] = "~/Downloads/df.scv") -> None:

    """See https://aws-sdk-pandas.readthedocs.io/en/latest/index.html"""

    boto3.setup_default_session(profile_name = aws_profile)

    logger = current_app.logger,
    logger.log(logging.INFO, 'Starting ingest_logs at {datetime.utcnow}')
    # source_connection_string = "s3://bioc-webstats-download-logs/data/year=2024/month=01/day=10/"  # TODO current_app.config["SOURCE LOCATION"]
    # df = wr.s3.read_parquet(source_connection_string, dataset=True)

    if start_date is None:
        start_date = db.WebstatsInfo.get_valid_thru_date() + timedelta(days=1)

    if end_date is None:
        end_date = (datetime.utcnow() - timedelta(days=1)).date()
        
    if start_date > end_date:
        logger.error("Start date ({start_date}) greater than end date ({end_date}). No log records ingested", 
                    start_date,
                    end_date)
        return
    if start_date == end_date:
        logger.warn("Start and End dates are both {start_date}. No log records ingested", 
                    start_date)
        return

    logger.info("Ingesting logs from ({start_date}) to ({end_date})",
                    start_date,
                    end_date)
        
    query_str = f"""
select  "date", "c-ip", "sc-status", "category", "package" from v_bioc_web_downloads
    where "date" between DATE '{strftime(start_date, "%Y-%m-%d")}' 
        and DATE '{strftime(end_date, "%Y-%m-%d")}'
"""
    result = wr.athena.read_sql_query(sql=query_str, database=source_database, ctas_approach=True)
    logger.info("{len(result)} records read")

    # Dump records to csv file if requested
    if result_filename is not None:
    # Write output to csv file
        result.to_csv(result_filename, index = False)
        logger.info("All records written to {result_filename}")
        return
    
    # Write out put to database table
    raise NotImplementedError
    # TODO DEBUG 
    result.to_sql('bioc_web_downloads', con=engine, if_exists='append', index=False)

#####################
# TODO Make this a SPROC ... get the start date from last update date.
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