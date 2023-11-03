# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest
from sqlalchemy import select

from bioc_webstats.models import PackageType, Stats, db_valid_thru_date

from .factories import StatsFactory

class TestStats:
    """Stats tests."""

    def test_db_valid_thru_date(self, db):
        """Verify appropriate last dtabase update date."""

        # Arrange
        expected = dt.date(2023, 10, 4)

        # Act
        result = db_valid_thru_date()

        # Assert
        assert result == expected

    def test_statsfactory_types(self, db):
        """Test stats factory."""
        # Arrange
        stats = StatsFactory()
        # Act
        db.session.commit()
        # Assert
        assert isinstance(stats.category, PackageType)
        assert str(stats.package)
        assert isinstance(stats.date, dt.date)
        assert bool(stats.is_monthly)
        assert int(stats.ip_count)
        assert int(stats.download_count)

    def test_stats_getall(self, db, stats):
        result = db.session.scalars(select(Stats)).all()
        # TODO compare stats to result
        assert stats == result

    def test_get_package_names(self, db, stats):
        # Arrange
        expected = ['BSgenome.Hsapiens.UCSC.hg38', 'BSgenome.Scerevisiae.UCSC.sacCer3', 'affy', 'affydata']

        # Act
        result = db.Stats.get_package_names()

        # Assert
        assert expected == result

    # TODO More tests using the stats ficture
    # TODO Threading problem with fixture?

    def test_get_download_counts_year(self, db, stats):
        # Arrange
        category = PackageType.BIOC
        pacakge = "affy"
        year = 2023
        expected = [
            Stats(
                category=PackageType.BIOC,
                package="affy",
                date=dt.date(2023, 9, 1),
                ip_count=10,
                download_count=20,
            ),
            Stats(
                category=PackageType.BIOC,
                package="affy",
                date=dt.date(2023, 10, 1),
                ip_count=20,
                download_count=40,
            ),
        ]

        result = Stats.get_download_counts(
            category=category, package=pacakge, year=year
        )

        # Assert
        assert repr(expected) == repr(result)

    def test_get_download_counts_full_year(self, db, stats):
        # Arrange
        #
        category = PackageType.ANNOTATION
        package = "BSgenome.Hsapiens.UCSC.hg38"
        year = 2022

        result = Stats.get_download_counts(
            category=category, package=package, year=year
        )

        # Assert
        # TODO CHeck the results (maybe with snapshot)
        assert True

    def test_get_download_counts_package(self, db, stats):
        # Arrange
        #
        category = PackageType.ANNOTATION
        package = "BSgenome.Hsapiens.UCSC.hg38"

        result = Stats.get_download_counts(category=category, package=package)

        # Assert
        # TODO CHeck the reulsts (maybe with snapshot)
        assert True

    def test_get_download_counts_category(self, db, stats):
        # Arrange
        #
        category = PackageType.BIOC
        expected = [
            Stats(
                category=PackageType.BIOC,
                package="affy",
                date="2023-09-01",
                ip_count=10,
                download_count=20,
            ),
            Stats(
                category=PackageType.BIOC,
                package="affy",
                date="2023-10-01",
                ip_count=20,
                download_count=40,
            ),
            Stats(
                category=PackageType.BIOC,
                package="affydata",
                date="2023-08-01",
                ip_count=30,
                download_count=60,
            ),
            Stats(
                category=PackageType.BIOC,
                package="affydata",
                date="2023-09-01",
                ip_count=40,
                download_count=80,
            ),
            Stats(
                category=PackageType.BIOC,
                package="affydata",
                date="2023-10-01",
                ip_count=50,
                download_count=100,
            ),
        ]

        result = Stats.get_download_counts(category=category)

        # Assert
        assert repr(expected) == repr(result)

    def test_get_download_scores(self, db, stats):
        # Arrange
        category = PackageType.BIOC
        expected = [('affy', 0, 2), ('affydata', 5, 1)]

        result = Stats.get_download_scores(category=category)

        # Assert
        assert result == expected
