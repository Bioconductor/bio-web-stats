"""Ingest download logs from Athena."""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

import awswrangler as wr
import boto3
import click
import pandas as pd
from flask import current_app

import bioc_webstats.aws_functions as aws_functions
import bioc_webstats.models as db


def ingest_logs(
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    aws_profile: Optional[chr] = None, 
    source_database: Optional[chr] = None,
    result_filename: Optional[chr] = None,
    cloudfront_id: Optional[chr] = None,
    cloudfront_path: Optional[chr] = None
    ) -> None:
    """Process download access logs"""

    """See https://aws-sdk-pandas.readthedocs.io/en/latest/index.html"""

    def datetime2str(dt: datetime) -> chr:
        """Conveninece function transform datetime into precise date and time string for logs"""
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # If an aws_profile value is specified, assume that we need to setup
    # the session
    if aws_profile is not None:
        boto3.setup_default_session(profile_name = aws_profile)
    # TODO this is a patch
    boto3.setup_default_session(region_name = 'us-east-1')
    log = current_app.logger
    log.log(logging.INFO, f'Starting ingest_logs at {datetime2str(datetime.utcnow())}')
    # source_connection_string = "s3://bioc-webstats-download-logs/data/year=2024/month=01/day=10/"  # TODO current_app.config["SOURCE LOCATION"]
    # df = wr.s3.read_parquet(source_connection_string, dataset=True)

    # TODO verify that we are not re-inserting existing dates

    if start_date is None:
        start_date = db.WebstatsInfo.get_valid_thru_date() + timedelta(days=1)

    if end_date is None:
        end_date = datetime.utcnow().date() - timedelta(days=1)
        
    if start_date > end_date:
        log.error(f"Start date {start_date} greater than end date {end_date}. No log records ingested", 
                    start_date,
                    end_date)
        return

    log.info(f"Ingesting logs from {start_date} to {end_date}")
        
    query_str = f"""
select  "date", "c-ip" as c_ip, "sc-status" as sc_status, "category", "package" from v_bioc_web_downloads
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
    db.BiocWebDownloads.insert_from_dataframe(dataframe=result)
    # TODO Report upload complete and give record count
    db.BiocWebDownloads.update_stats_from_downloads(start_date.replace(day=1))
    # TODO reuport update_stats complete
    
    if cloudfront_id is None:
        log.info("Cache invalidation skipped")
    else:
        log.info(f"CloudFront ditribution {cloudfront_id}/{cloudfront_path} invalidation started")
        aws_functions.cloudfront_invalidation(cloudfront_id, [cloudfront_path])
        # TODO report invalidation result

    log.info("Log ingestion complete")
