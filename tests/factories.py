# -*- coding: utf-8 -*-
"""Factories to help in tests."""
import datetime as dt

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory

from bioc_webstats.database import db
from bioc_webstats.models import Packages, PackageType, Stats, WebstatsInfo


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class WebstatsInfoFactory(BaseFactory):
    """WebstatsInfo factory."""

    key = "ValidThru"
    value = "2023-10-04"

    class Meta:
        """Factory configuration."""

        model = WebstatsInfo


class StatsFactory(BaseFactory):
    """Stats factory."""
    
    package = Sequence(lambda n: f"pack{n}")
    date = Sequence(lambda n: dt.date(2015, 1, 1) + dt.timedelta(days=n))
    is_monthly = True
    ip_count = Sequence(lambda n: (n + 1) * 10)
    download_count = Sequence(lambda n: (n + 1) * 20)

    class Meta:
        """Factory configuration."""

        model = Stats


class PackagesFactory(BaseFactory):
    """Stats factory."""

    class Meta:
        """Factory configuration."""

        model = Packages
