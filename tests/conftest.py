# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import datetime as dt
import logging

import pytest
from dateutil.relativedelta import relativedelta
from factory import Sequence
from webtest import TestApp

from bioc_webstats.app import create_app
from bioc_webstats.database import db as _db
from bioc_webstats.models import PackageType, db_valid_thru_date

from .factories import StatsFactory


@pytest.fixture(scope="function")
def app():
    """Create application for the tests."""
    _app = create_app("tests.settings")
    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="function")
def testapp(app):
    """Create Webtest app."""
    return TestApp(app)


@pytest.fixture(scope="function")
def db(app):
    """Create database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


database_test_cases = [
    (PackageType.BIOC, "affy", "2023-09-01"),
    (PackageType.BIOC, "affydata", "2023-08-01"),
    (PackageType.ANNOTATION, "BSgenome.Hsapiens.UCSC.hg38", "2019-01-01"),
    (PackageType.ANNOTATION, "BSgenome.Scerevisiae.UCSC.sacCer3", "2021-01-01"),
]

def generate_small_test_db_stats():
    """Create list of StatsFactory objects for small test database."""

    # TODO Mock EndDate?
    end_date = db_valid_thru_date()

    def months_sequence(start_date: dt.date, end_date: dt.date):
        """Yield the first day of each month from start_date to end_date inclusive."""
        current_date = start_date

        while current_date <= end_date:
            yield current_date
            current_date += relativedelta(months=1)

    stats = [
        StatsFactory(
            category=category,
            package=package,
            date=d,
            is_monthly=True,
            ip_count=Sequence(lambda n: (n + 1) * 10),
            download_count=Sequence(lambda n: (n + 1) * 20),
        )
        for category, package, start_date in database_test_cases
        for d in months_sequence(
            dt.datetime.strptime(start_date, "%Y-%m-%d").date(), end_date
        )
    ]
    return stats


@pytest.fixture(scope="function")
def stats(db):
    """Create stats for the tests."""

    stats = generate_small_test_db_stats()
    db.session.commit()
    return stats
