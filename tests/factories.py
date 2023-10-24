# -*- coding: utf-8 -*-
"""Factories to help in tests."""
import datetime as dt

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bioc_webstats.database import db
from bioc_webstats.models import PackageType, Stats


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class StatsFactory(BaseFactory):
    """Stats factory."""

    category = PackageType.BIOC
    package = Sequence(lambda n: f"pack{n}")
    date = Sequence(lambda n: dt.date(2015, 1, 1) + dt.timedelta(days=n))
    is_monthly = True
    ip_count = Sequence(lambda n: (n + 1) * 10)
    download_count = Sequence(lambda n: (n + 1) * 20)

    class Meta:
        """Factory configuration."""

        model = Stats
