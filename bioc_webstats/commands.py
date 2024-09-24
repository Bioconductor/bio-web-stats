# -*- coding: utf-8 -*-
"""Click commands."""
import os
from datetime import date, datetime
from glob import glob
import logging
from subprocess import call

import boto3
import click

from flask import current_app
from bioc_webstats.ingest_logs import ingest_logs
from bioc_webstats.packages_table_update import packages_table_update
from bioc_webstats.configmodule import configuration_dictionary

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


def parse_date(ctx, param, value):
    """Helper for parsing click.option dates"""
    if value is None:
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise click.BadParameter("Date should be in YYYY-MM-DD format.")


@click.command()
@click.option(
    "-c/-C",
    "--coverage/--no-coverage",
    default=True,
    is_flag=True,
    help="Show coverage report",
)
def test(coverage):
    """Run the tests."""
    import pytest

    args = [TEST_PATH, "--verbose"]
    if coverage:
        args.append("--cov=bioc_webstats")
    rv = pytest.main(args)
    exit(rv)


@click.command()
@click.option(
    "-f",
    "--fix-imports",
    default=True,
    is_flag=True,
    help="Fix imports using isort, before linting",
)
@click.option(
    "-c",
    "--check",
    default=False,
    is_flag=True,
    help="Don't make any changes to files, just confirm they are formatted correctly",
)
def lint(fix_imports, check):
    """Lint and check code style with black, flake8 and isort."""
    skip = ["node_modules", "requirements", "migrations"]
    root_files = glob("*.py")
    root_directories = [
        name for name in next(os.walk("."))[1] if not name.startswith(".")
    ]
    files_and_directories = [
        arg for arg in root_files + root_directories if arg not in skip
    ]

    def execute_tool(description, *args):
        """Execute a checking tool with its arguments."""
        command_line = list(args) + files_and_directories
        click.echo(f"{description}: {' '.join(command_line)}")
        rv = call(command_line)
        if rv != 0:
            exit(rv)

    isort_args = []
    black_args = []
    if check:
        isort_args.append("--check")
        black_args.append("--check")
    if fix_imports:
        execute_tool("Fixing import order", "isort", *isort_args)
    execute_tool("Formatting style", "black", *black_args)
    execute_tool("Checking code style", "flake8")


@click.command()
def gendb():
    """Generate small test database."""
    from bioc_webstats.database import db
    from tests.conftest import generate_small_test_db

    click.echo("Creating small test database")
    app = current_app._get_current_object()

    test_db_contents = generate_small_test_db(app)
    pass


@click.command()
@click.option(
    "-s",
    "--start",
    required=False,
    callback=parse_date,
    help="Beginning date for upload. Default: first date not already proceessed.",
)
@click.option(
    "-e",
    "--end",
    required=False,
    callback=parse_date,
    help="Ending date for upload. Default: yesterday (UTC)",
)
@click.option(
    "-d",
    "--database",
    required=False,
    help="Name of the source database. DefaUlt: default",
)
@click.option(
    "-f",
    "--filename",
    required=False,
    help="Specifies the name of a local file to receive the csv results instead of sending them to the database",
)
@click.option(
    "-c",
    "--cloudfront",
    required=False,
    help="If present, the distribution ID of the CloudFront cachce to refresh. If absent, no refresh",
)
@click.option(
    "--path",
    required=False,
    help="The CloudFront path to refresh. Default: '/packages/stats/*'",
)
def ingest(start, end, database, filename, cloudfront, path):
    """Read raw weblogs, select valid package downlads, update webstats database"""

    if path is None:
        path = "/packages/stats/*"

    ingest_logs(
        start_date=start,
        end_date=end,
        source_database=database,
        result_filename=filename,
        cloudfront_id=cloudfront,
        cloudfront_path=path,
    )


@click.command()
@click.option(
    "-n", "--namespace", required=False, help="Namespace (parameter path prefix)"
)
@click.option("-p", "--profile", required=False, help="AWS SSO profile for target")
@click.option("-r", "--region", required=False, help="AWS target region")
def configp(namespace, profile, region):
    """Initialize AWS parameter set"""

    if namespace is None:
        namespace = '/bioc/webstats/prod/'
    if region is None:
        region = 'us-east-1'
    if profile is None:
        profile = 'bioc'

    session = boto3.Session(
        profile_name=profile,
        region_name=region
    )

    ssm_client = session.client('ssm')

    # TODO Test for previously existing. Create --force parameter
    # TODO Add tags
    
    try:
        for p in configuration_dictionary:
            q = p
            q["Name"] = namespace + p["Name"]
            response = ssm_client.put_parameter(**q)
            # TODO check response for errors
    except Exception as e:
        logging.error(f"Failed to store parameters. {e}")
        raise e
    logging.info("AWs Parameter set configured namespace:{namespace} profile:{profile} {region}.")

@click.command()
@click.option("-d", "--dry_run", is_flag=True, required=False, help="Report packages changes but do not update database")
@click.option("-v", "--verbose", is_flag=True, required=False, help="More reporting")
@click.option("-f", "--force", is_flag=True, required=False, help="Update table even though the update is suspicously large")
def packages(dry_run:bool = False, verbose: bool = True, force: bool = False):
    """Read package information from the Bioconductor infrastructure and update the packages table to reflect current status"""

    packages_table_update(dry_run, verbose, force)
