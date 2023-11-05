"""Model unit tests."""
import datetime as dt

import pytest
from sqlalchemy import select

from bioc_webstats.models import PackageType, Stats, db_valid_thru_date, list_to_dict

from .conftest import check_hashed_count_list


@pytest.mark.usefixtures("db")
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

    def test_get_package_names(self, stats):
        """Get the complete list of package names in collation sequence."""
        # Arrange
        expected = sorted({u["package"] for u in stats})

        # Act
        result = Stats.get_package_names()

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

        result = Stats.get_download_counts(category=category, package=package)

        # Assert
        assert result == expected

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
