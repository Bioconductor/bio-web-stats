# conftest.py
# See https://github.com/Jedylemindee/articles/blob/98d163ee70f47b9a8b6fc1f9736822b13defe5ea/flask-pytest.md

import datetime as dt

import pytest
from dateutil.relativedelta import relativedelta
from factory import Sequence
from flask_migrate import upgrade as flask_migrate_upgrade

from bioc_webstats.app import create_app
from bioc_webstats.extensions import db as _db
from bioc_webstats.models import PackageType, db_valid_thru_date

from .factories import StatsFactory


@pytest.fixture(scope="session")
def app():
    app = create_app("../tests/settings.py")
    with app.app_context():
        _db.create_all()
        generate_small_test_db_stats()
        
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


@pytest.fixture(scope="session")
def stats(db):
    """Create stats for the tests."""

    return generate_small_test_db_stats()
