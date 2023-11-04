# conftest.py
# See https://github.com/Jedylemindee/articles/blob/98d163ee70f47b9a8b6fc1f9736822b13defe5ea/flask-pytest.md

import datetime as dt
import logging
import math
from zlib import crc32

import pytest
from dateutil.relativedelta import relativedelta

from bioc_webstats.app import create_app
from bioc_webstats.extensions import db as _db
from bioc_webstats.models import PackageType, db_valid_thru_date

from .factories import StatsFactory


@pytest.fixture(scope="session")
def app():
    app = create_app("../tests/settings.py")
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG) # TODO Improve
    with app.app_context():
        _db.create_all()
        u = generate_small_test_db_stats()
        [StatsFactory(**v) for v in u]
        yield app

@pytest.fixture(scope="function")
def test_client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def db(app, request):
    """Session-wide test database."""

    def teardown():
        _db.drop_all()
    _db.app = app

    # TODO Evaluate the need for this
    # flask_migrate_upgrade(directory="migrations")
    # request.addfinalizer(teardown)
    return _db

@pytest.fixture(scope="function")
def session(db, request):
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


def generate_small_test_db_stats():
    """Create list of dictionary objects corresponding to Stats columns for small test database."""

    # TODO Mock EndDate?
    end_date = db_valid_thru_date()

    def months_sequence(start_date: dt.date, end_date: dt.date):
        """Yield the first day of each month from start_date to end_date inclusive."""
        current_date = start_date

        while current_date <= end_date:
            yield current_date
            current_date += relativedelta(months=1)

    stats_dict = []
    for category, package, start_date in database_test_cases:
        for d in months_sequence(dt.datetime.strptime(start_date, "%Y-%m-%d").date(), end_date):
            u = {
                'category': category,
                'package': package,
                'date': d,
                'is_monthly': True
            }

            s = '|'.join(str(value) for value in u.values())
            crc = crc32(s.encode('utf-8')) % 9007
            u["ip_count"] = int(math.ceil(math.sqrt(crc)))
            u["download_count"] = crc
            stats_dict.append(u)

    return stats_dict


@pytest.fixture(scope="session")
def stats(db):
    """Create stats for the tests."""

    return generate_small_test_db_stats()
