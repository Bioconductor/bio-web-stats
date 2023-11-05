# conftest.py
# See https://github.com/Jedylemindee/articles/blob/98d163ee70f47b9a8b6fc1f9736822b13defe5ea/flask-pytest.md

import datetime as dt
import logging
import math
from zlib import crc32

import pytest
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from bioc_webstats.app import create_app
from bioc_webstats.extensions import db as _db
from bioc_webstats.models import PackageType, db_valid_thru_date

from .factories import StatsFactory


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    _app = create_app("../tests/settings.py")
    create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    _app.logger.setLevel(logging.DEBUG)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()

@pytest.fixture(scope="function")
def test_client(app):
    return app.test_client()

@pytest.fixture(scope="session")
def db(app):
    """Session-wide test database."""

    _db.app = app
    with app.app_context():
        _db.create_all()
        u = generate_small_test_db_stats()
        [StatsFactory(**v) for v in u]
        _db.session.commit()

    yield _db

    _db.session.close()
    _db.drop_all()


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

def create_hashed_counts(d: dict) -> (int, int):
    """Calculate reproducable hashed ip_count and download_count values for test stats rows.

    For small database tests, create ip_count and downlooad count values that are a function of the
    other columns of the stats table. This function is used to both generate the test rows and to check
    that the test rows return the correct values.

    Arguments:
        d -- A dictionary containing the tvalues of a stats record

    Returns:
        an ordered pair, the hashed ip_count and the hashed download_count
    """

    s = '|'.join([str(d.get(tag, "")) for tag in ["category", "package", "date", "is_monthly"]])
    # 9007 is a prime number of a size to give a reasonable hash for test purposes
    download_count = crc32(s.encode('utf-8')) % 9007
    ip_count = int(math.ceil(math.sqrt(download_count)))
    return (ip_count, download_count)

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
            u["ip_count"], u["download_count"] = create_hashed_counts(u)
            stats_dict.append(u)

    return stats_dict


def check_hashed_counts(d: dict) -> bool:
    ip_count, download_count = create_hashed_counts(d)
    return d.get("ip_count", -1) == ip_count and d.get("download_count", -1) == download_count


def check_hashed_count_list(d_list: [dict]) -> bool:
    for r in d_list:
        if not check_hashed_counts(r):
            return False
    return True


@pytest.fixture(scope="session")
def stats(db):
    """Create stats for the tests."""

    return generate_small_test_db_stats()
