"""Model unit tests."""
import datetime as dt

import pytest
from sqlalchemy import select

from bioc_webstats.models import (
    Packages,
    PackageType,
    Stats,
    WebstatsInfo,
    list_to_dict,
)

from .conftest import check_hashed_count_list


@pytest.mark.usefixtures("db")
class TestStats:
    """Stats tests."""

    def test_db_valid_thru_date(self, webstatsinfo):
        """Verify appropriate last dtabase update date."""
        # Arrange
        expected = dt.date(2023, 10, 4)

        # Act
        result = WebstatsInfo.get_valid_thru_date()

        # Assert
        assert result == expected

    def test_statsfactory_types(self, db):
        """Test stats factory."""
        # Arrange

        # Act
        results = db.session.execute(select(Stats))
        result = next(results, None)[0]

        # Assert
        assert isinstance(result.category, PackageType)
        assert str(result.package)
        assert isinstance(result.date, dt.date)
        assert bool(result.is_monthly)
        assert int(result.ip_count)
        assert int(result.download_count)

    def test_stats_getall(self, db, stats):
        """Compare contents of stats table with the list of dictionaries from which it was created."""
        # Arrange

        # Act
        result = db.session.scalars(select(Stats))
        result = list_to_dict(result)

        # Assert
        assert check_hashed_count_list(result)
        assert stats == result

    def test_get_package_names(self, packages):
        """Get the complete list of package names in collation sequence."""
        # Arrange
        expected = sorted(packages)

        # Act
        result = Packages.get_package_names()

        # Assert
        assert expected == result

    # TODO Review database return values for consistency
    # TODO Verify that we only want dates and counts for this function
    def test_get_download_counts_year(self, stats):
        """Select category, package and year."""
        category = PackageType.BIOC
        package = "affy"
        year = 2023
        expected = [(x["date"], x["ip_count"], x["download_count"]) for x in stats
                    if x["category"] == category and x["package"] == package and x["date"].year == year]

        result = Stats.get_download_counts(category=category, package=package, year=year)

        # Assert
        assert expected == result

    def test_get_download_counts_full_year(self, stats):
        """Select one full year of download counts."""
        # Arrange
        #
        category = PackageType.ANNOTATION
        package = "BSgenome.Hsapiens.UCSC.hg38"
        year = 2022
        expected = [(d["date"], d["ip_count"], d["download_count"]) for d in stats
                    if d["category"] == category and d["package"] == package and d["date"].year == year]

        result = Stats.get_download_counts(
            category=category, package=package, year=year
        )

        # Assert
        assert result == expected

    def test_get_download_counts_package(self, stats):
        """Select all the download counts for a given package."""
        # Arrange
        #
        category = PackageType.ANNOTATION
        package = "BSgenome.Hsapiens.UCSC.hg38"
        expected = [(d["date"], d["ip_count"], d["download_count"]) for d in stats
                    if d["category"] == category and d["package"] == package]


        result_hi_first = Stats.get_download_counts(category=category, package=package, newest_year_first=True)
        result_lo_first = Stats.get_download_counts(category=category, package=package, newest_year_first=False)

        # Assert
        expected_hi = sorted(expected, key=lambda x: x[0], reverse=True)
        assert result_hi_first == expected_hi

        expected_lo = sorted(expected, key=lambda x: x[0], reverse=False)
        assert result_lo_first == expected_lo

    def test_get_download_counts_category(self, stats):
        """Select all the download counts for a given category."""
        # Arrange
        category = PackageType.BIOC
        expected = [(d["package"], d["date"], d["ip_count"], d["download_count"])
                    for d in stats if d["category"] == category]

        result = Stats.get_download_counts(category=category)

        # Assert
        assert result == expected

    def test_get_download_scores(self, stats):
        """Select all the scores for a given category."""
        # Arrange
        category = PackageType.BIOC
        expected = [('affy', 2, 2), ('affydata', 7, 1)]

        result = Stats.get_download_scores(category=category)

        # Assert
        assert result == expected
