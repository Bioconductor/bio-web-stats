# -*- coding: utf-8 -*-
"""Click commands."""
import os
from glob import glob
from subprocess import call
from flask import current_app

import click

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


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
    from tests.conftest import generate_small_test_db_stats

    click.echo("Creating small test database")
    generate_small_test_db_stats()
    db.session.commit()
    

@click.command('ingest')
def ingest():
    """Ingest download logs from Athena.
    See https://aws-sdk-pandas.readthedocs.io/en/latest/index.html
    """
    from sqlalchemy import create_engine
    import pandas as pd
    import awswrangler as wr
    db_connection_string = current_app.config["SQLALCHEMY_DATABASE_URI"]
    source_connection_string = "s3://bioc-webstats-download-logs/data/year=2024/month=01/day=10/"  # TODO current_app.config["SOURCE LOCATION"]
    df = wr.s3.read_parquet(source_connection_string, dataset=True)
    engine = create_engine(db_connection_string)
    foo = df.to_sql('bioc_web_downloads1', engine)
    pass

