"""Ingest download logs from Athena."""

from typing import Optional
import click
from datetime import date, timedelta, datetime
import pandas as pd
import boto3
import awswrangler as wr
from flask import current_app
import logging

import bioc_webstats.models as db
from flask.cli import with_appcontext

def ingest_logs(
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    aws_profile: Optional[chr] = "bioc",
    source_database: Optional[chr] = None,
    result_filename: Optional[chr] = None) -> None:
    """Process download access logs"""

    """See https://aws-sdk-pandas.readthedocs.io/en/latest/index.html"""

    def datetime2str(dt: datetime) -> chr:
        """Conveninece function transform datetime into precise date and time string for logs"""
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # If an aws_profile value is specified, assume that we need to setup
    # the session
    if aws_profile is not None:
        boto3.setup_default_session(profile_name = aws_profile)

    log = current_app.logger
    log.log(logging.INFO, f'Starting ingest_logs at {datetime2str(datetime.utcnow())}')
    # source_connection_string = "s3://bioc-webstats-download-logs/data/year=2024/month=01/day=10/"  # TODO current_app.config["SOURCE LOCATION"]
    # df = wr.s3.read_parquet(source_connection_string, dataset=True)

    if start_date is None:
        start_date = db.WebstatsInfo.get_valid_thru_date() + timedelta(days=1)

    if end_date is None:
        end_date = datetime.utcnow().date() - timedelta(days=1)
        
    if start_date > end_date:
        log.error(f"Start date {start_date} greater than end date {end_date}. No log records ingested", 
                    start_date,
                    end_date)
        return
    if start_date == end_date:
        log.warn(f"Start and End dates are both {start_date}. No log records ingested", 
                    start_date)
        return

    log.info(f"Ingesting logs from {start_date} to {end_date}")
        
    query_str = f"""
select  "date", "c-ip", "sc-status", "category", "package" from v_bioc_web_downloads
    where "date" between DATE '{start_date.strftime( "%Y-%m-%d")}' 
        and DATE '{end_date.strftime("%Y-%m-%d")}'
"""
    if source_database is None:
        source_database = "default"

    # TODO try/except protection
    result = wr.athena.read_sql_query(sql=query_str, database=source_database, ctas_approach=True)
    log.info(f"{len(result)} records read")

    # Dump records to csv file if requested
    if result_filename is not None:
    # Write output to csv file
        result.to_csv(result_filename, index = False)
        log.info(f"All records written to {result_filename}")
        return
    
    # Write out put to database table
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