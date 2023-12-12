# -*- coding: utf-8 -*-
"""Stats models."""

import datetime as dt
import enum
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    Enum,
    String,
    and_,
    asc,
    desc,
    extract,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column

from bioc_webstats.database import Model, db


class PackageType(enum.Enum):
    """The major categories for packages as an enum, with enum values as their human-readable forms."""

    BIOC = "bioc"
    EXPERIMENT = "experiment"
    ANNOTATION = "annotation"
    WORKFLOWS = "workflows"


def package_type_exists(value: str) -> bool:
    """Is a string a valid PackageType."""
    return value in [e.value for e in PackageType]


def list_to_dict(u) -> [dict]:
    """Transform list of sqlalchemy results to list of dictionaries."""
    return [v.as_dict() for v in u]


class WebstatsInfo(Model):
    """Table of state information and application metadata."""

    key: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        comment="Metadata key."
    )
    value: Mapped[str] = mapped_column(
        String,
        nullable=True,
        comment="Metadata value."
    )

    from sqlalchemy.ext.declarative import declarative_base

    @staticmethod
    def get_valid_thru_date() -> dt.date:
        """Retrieve date the database was last upated."""
        x = db.session.scalars(
            select(WebstatsInfo.value).where(WebstatsInfo.key == "ValidThru")
        ).fetchall()[0]  # TODO fetch first
        return dt.datetime.strptime(x, "%Y-%m-%d").date()


class Packages(Model):
    """All Package Names from git.bioconductor.org."""

    package: Mapped[str] = mapped_column(String, primary_key=True)

    @staticmethod
    def get_package_names():
        """Return all the package names."""
        return db.session.scalars(
            select(Packages.package).order_by(Packages.package.asc())
        ).fetchall()


class Stats(Model):
    """Create table of summary statistics."""

    category: Mapped[PackageType] = mapped_column(Enum(PackageType), primary_key=True)
    package: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[dt.date] = mapped_column(
        Date,
        primary_key=True,
        comment="Dates repesenting months always have day=1, while years have month=12 and day=31",
    )
    is_monthly: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="If true, date span is 1 month, if false, 1 year",
    )
    ip_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    download_count: Mapped[int] = mapped_column(BigInteger, nullable=False)

    from sqlalchemy.ext.declarative import declarative_base

    def __repr__(self):
        """_summary_.

        Returns:
            _description_
        """
        return (
            f"Stats(category={self.category}, package='{self.package}', "
            f"date='{self.date}', ip_count={self.ip_count}, "
            f"download_count={self.download_count})"
        )

    @staticmethod
    def get_download_counts(
        category: PackageType, package: Optional[str] = None, year: Optional[int] = None
    ):
        """_summary_.

        Arguments:
            category -- _description_

        Keyword Arguments:
            package -- _description_ (default: {None})
            year -- _description_ (default: {None})

        Returns:
            _description_
        """
        where_clause = [Stats.category == category]
        select_clause = [Stats.date, Stats.ip_count, Stats.download_count]
        if package is not None:
            where_clause.append(Stats.package == package)
        else:
            select_clause = [Stats.package] + select_clause
        if year is not None:
            where_clause.append(extract("year", Stats.date) == year)

        final_where_clause = and_(*where_clause)

        # Execute query
        text = (
            select(*select_clause)
            .where(final_where_clause)
            .order_by(asc(Stats.package), desc(extract("year", Stats.date)), asc(Stats.date))
        )

        result = db.session.execute(text).fetchall()
        return result

    # TODO annual count must be computed seperately for "all packages in category"
    # because distinct IP's is over the category
    @staticmethod
    def get_combined_counts(category: PackageType):
        """Get counts combined for all packages in a given category.

        TODO Returning ip_counts as sum of the packages, but must
            be distinct across all the packages.
            Database changes needed

        Arguments:
            category -- The category

        Returns:
            _description_
        """
        result = db.session.execute(
            select(
                Stats.date,
                # TODO See TODO at head of method
                func.sum(Stats.ip_count).label("ip_count"),
                func.sum(Stats.download_count).label("download_count"),
            )
            .where(Stats.category == category)
            .group_by(Stats.date)
            .order_by(desc(extract("year", Stats.date)), asc(Stats.date))
        )

        return result.fetchall()

    @staticmethod
    def get_download_scores(category: PackageType) -> [(str, int, int)]:
        """Return a download score for each package.

        The rank is an ordinal that indicates relative activity.
        Rank = 1 is the most downloaded package in the category, Raank=2 is next, etc.

        The score is the average of the number of monthly distinct IP's (ip_count)
        for each of the 12 prior complete months, regardless of when the package
        was acessioned. That is, the last month in the date range is the month
        prior to the current date and the first month of the date range is
        12 months prior the the current date. Because missing rows are taken as
        having an IP_count of 0, the score is the sum of all the Stats rows
        in range for the given package divided by 12 (as opposed the mean).

        Arguments:
            category -- only packages of this Package.Type will be selected

        Keyword Arguments:
            package -- A string indicting the package to be selected
            If None, then all the packages of the given category are selected

        Returns:
            A list of tuples (package_name, score, rank) where rank is the
            numerical rank of the the scores. The results are sorted by package name.
        """
        x = WebstatsInfo.get_valid_thru_date()
        # the first of the current month
        y = dt.date(x.year, x.month, 1)
        # the last day of the prior month
        end_date = y - relativedelta(days=1)
        # the first day of the date 1 year before the end date
        start_date = y - relativedelta(months=12)

        result = db.session.execute(
            select(
                Stats.package,
                (func.sum(Stats.ip_count) // 12).label("score"),
                func.rank()
                .over(order_by=func.sum(Stats.ip_count).desc())
                .label("rank"),
            )
            .where(
                and_(
                    Stats.category == category,
                    Stats.date.between(start_date, end_date),
                )
            )
            .group_by(Stats.package)
            .order_by(asc(Stats.package))
        )
        return result.fetchall()


class CategoryStats(Model):
    """Create table of summary statistics."""

    category: Mapped[PackageType] = mapped_column(Enum(PackageType), primary_key=True)
    date: Mapped[dt.date] = mapped_column(
        Date,
        primary_key=True,
        comment="Dates repesenting months always have day=1, while years have month=12 and day=31",
    )
    is_monthly: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="If true, date span is 1 month, if false, 1 year",
    )
    ip_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    download_count: Mapped[int] = mapped_column(BigInteger, nullable=False)

    from sqlalchemy.ext.declarative import declarative_base

    def __repr__(self):
        """_summary_.

        Returns:
            _description_
        """
        return (
            f"CategoryStats(category={self.category}, "
            f"date='{self.date}', ip_count={self.ip_count}, "
            f"download_count={self.download_count})"
        )

    @staticmethod
    def get_download_counts(
        category: PackageType, year: Optional[int] = None
    ):
        """_summary_.

        Arguments:
            category -- _description_

        Keyword Arguments:
            package -- _description_ (default: {None})
            year -- _description_ (default: {None})

        Returns:
            _description_
        """
        where_clause = [CategoryStats.category == category]  # TODO
        select_clause = [CategoryStats.date, CategoryStats.ip_count, CategoryStats.download_count]
        if year is not None:
            where_clause.append(extract("year", CategoryStats.date) == year)

        final_where_clause = and_(*where_clause)

        # Execute query
        text = (
            select(*select_clause)
            .where(final_where_clause)
            .order_by(desc(extract("year", CategoryStats.date)), asc(CategoryStats.date))
        )

        result = db.session.execute(text).fetchall()
        return result

    # TODO annual count must be computed seperately for "all packages in category"
    # because distinct IP's is over the category
    @staticmethod
    def get_combined_counts(category: PackageType):
        """Get counts combined for all packages in a given category.

        TODO Returning ip_counts as sum of the packages, but must
            be distinct across all the packages.
            Database changes needed

        Arguments:
            category -- The category

        Returns:
            _description_
        """
        result = db.session.execute(
            select(
                CategoryStats.date,
                func.sum(CategoryStats.ip_count).label("ip_count"),
                func.sum(CategoryStats.download_count).label("download_count"),
            )
            .where(CategoryStats.category == category)
            .group_by(CategoryStats.date)
            .order_by(desc(extract("year", CategoryStats.date)), asc(CategoryStats.date))
        )

        return result.fetchall()

    @staticmethod
    def get_download_scores(category: PackageType) -> [(str, int, int)]:
        """Return a download score for each package.

        The rank is an ordinal that indicates relative activity.
        Rank = 1 is the most downloaded package in the category, Raank=2 is next, etc.

        The score is the average of the number of monthly distinct IP's (ip_count)
        for each of the 12 prior complete months, regardless of when the package
        was acessioned. That is, the last month in the date range is the month
        prior to the current date and the first month of the date range is
        12 months prior the the current date. Because missing rows are taken as
        having an IP_count of 0, the score is the sum of all the CategoryStats rows
        in range for the given package divided by 12 (as opposed the mean).

        Arguments:
            category -- only packages of this Package.Type will be selected

        Keyword Arguments:
            package -- A string indicting the package to be selected
            If None, then all the packages of the given category are selected

        Returns:
            A list of tuples (package_name, score, rank) where rank is the
            numerical rank of the the scores. The results are sorted by package name.
        """
        x = WebstatsInfo.get_valid_thru_date()
        # the first of the current month
        y = dt.date(x.year, x.month, 1)
        # the last day of the prior month
        end_date = y - relativedelta(days=1)
        # the first day of the date 1 year before the end date
        start_date = y - relativedelta(months=12)

        result = db.session.execute(
            select(
                (func.sum(CategoryStats.ip_count) // 12).label("score"),
                func.rank()
                .over(order_by=func.sum(CategoryStats.ip_count).desc())
                .label("rank"),
            )
            .where(
                and_(
                    CategoryStats.category == category,
                    CategoryStats.date.between(start_date, end_date),
                )
            )
            .group_by(CategoryStats.package)
            .order_by(asc(CategoryStats.package))
        )
        return result.fetchall()
