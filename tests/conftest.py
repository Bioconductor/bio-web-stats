"""Initialization for pytests."""
import datetime as dt
import logging
import math
from zlib import crc32

import pytest
from dateutil.relativedelta import relativedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from webtest import TestApp

from bioc_webstats.app import create_app
from bioc_webstats.extensions import db as _db
from bioc_webstats.models import PackageType

from .factories import PackagesFactory, StatsFactory, WebstatsInfoFactory


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    _app = create_app("debug")
    create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    _app.logger.setLevel(logging.DEBUG)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="session")
def db(app: Flask):
    """Session-wide test database."""
    _db.app = app
    with app.app_context():
        _db.create_all()
        u = generate_small_test_db_stats()
        [StatsFactory(**v) for v in u]
        u = [{"key": "ValidThru", "value": "2023-10-04"}]
        [WebstatsInfoFactory(**v) for v in u]
        [PackagesFactory(**v) for v in generate_small_test_db_packages()]
        _db.session.commit()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture(scope="session")
def webapp(app: Flask, db: SQLAlchemy):
    """Fixture for app test."""
    return TestApp(app)


@pytest.fixture(scope="function")
def session(db: SQLAlchemy, request: pytest.FixtureRequest):
    """Create isolated transaction."""
    db.session.begin_nested()

    def commit():
        db.session.flush()

    # patch commit method
    old_commit = db.session.commit
    db.session.commit = commit

    def teardown():
        db.session.rollback()
        db.session.close()
        db.session.commit = old_commit

    request.addfinalizer(teardown)
    return db.session


database_test_cases = [
    (PackageType.BIOC, "affy", "2023-09-01"),
    (PackageType.BIOC, "affydata", "2023-08-01"),
    (PackageType.ANNOTATION, "BSgenome.Hsapiens.UCSC.hg38", "2019-01-01"),
    (PackageType.ANNOTATION, "BSgenome.Scerevisiae.UCSC.sacCer3", "2021-01-01"),
]

database_test_valid_date = dt.date(2023, 10, 4)


def create_hashed_counts(d: dict) -> tuple[int, int]:
    """Calculate reproducable hashed ip_count and download_count values for test stats rows.

    For small database tests, create ip_count and downlooad count values that are a function of the
    other columns of the stats table. This function is used to both generate the test rows and to check
    that the test rows return the correct values.

    Arguments:
        d -- A dictionary containing the tvalues of a stats record

    Returns:
        an ordered pair, the hashed ip_count and the hashed download_count
    """
    s = "|".join(
        [str(d.get(tag, "")) for tag in ["category", "package", "date", "is_monthly"]]
    )
    # 9007 is a prime number of a size to give a reasonable hash for test purposes
    download_count = crc32(s.encode("utf-8")) % 9007
    ip_count = int(math.ceil(math.sqrt(download_count)))
    return (ip_count, download_count)


def generate_small_test_db_packages():
    """Create list of package names in the small_test database."""
    packages_dict = []
    for category, package, _ in database_test_cases:
        u = {
            "category": category,
            "package": package,
            "first_version": 201,
            "last_version": None,
        }
        packages_dict.append(u)
    return packages_dict


def generate_small_test_db_stats():
    """Create list of dictionary objects corresponding to Stats columns for small test database."""
    end_date = database_test_valid_date

    def months_sequence(start_date: dt.date, end_date: dt.date):
        """Yield the first day of each month from start_date to end_date inclusive."""
        current_date = start_date

        while current_date <= end_date:
            yield current_date
            current_date += relativedelta(months=1)

    stats_dict = []
    for category, package, start_date in database_test_cases:
        for d in months_sequence(
            dt.datetime.strptime(start_date, "%Y-%m-%d").date(), end_date
        ):
            u = {
                "category": category,
                "package": package,
                "date": d,
                "is_monthly": True,
            }
            u["ip_count"], u["download_count"] = create_hashed_counts(u)
            stats_dict.append(u)

    return stats_dict


def check_hashed_counts(d: dict) -> bool:
    """Check that a genearted test data with hashed counts are correct.

    Arguments:
        d -- Dictionary form of stats table row

    Returns:
        True ==> The ip_count and download_count matches the calcuated hash
    """
    ip_count, download_count = create_hashed_counts(d)
    return (
        d.get("ip_count", -1) == ip_count
        and d.get("download_count", -1) == download_count
    )


def check_hashed_count_list(d_list: list[dict]) -> bool:
    """
    This function checks if all stats rows in a list have the expected hash counts.
    
    :param d_list: A list of dictionaries derived from Stats Rows
    :type d_list: [dict]
    :return: The function `check_hashed_hashed_count_list` returns a boolean value. It returns `True` if
    all the rows in the input list have the expected count values, and it returns `False` if at least
    one row has an incorrect count value.
    """
    """Check that all stats rows in this list have expected hash counts.

    Arguments:
        d_list -- A list of dictionaries derivd from Stats Rows.

    Returns:
        True ==> All the rows have the expected count values.
        False ==> At least one row was incorrect.
    """
    for r in d_list:
        if not check_hashed_counts(r):
            return False
    return True


@pytest.fixture(scope="session")
def webstatsinfo(db: SQLAlchemy):
    """Create WebstatsInfo for the tests."""
    return


@pytest.fixture(scope="session")
def stats(db: SQLAlchemy):
    """Create stats for the tests."""
    return generate_small_test_db_stats()


@pytest.fixture(scope="session")
def packages(db: SQLAlchemy):
    """Create packages for the tests."""
    return [u['package'] for u in generate_small_test_db_packages()]
