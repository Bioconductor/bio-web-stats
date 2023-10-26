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
    extract,
    func,
    select,
)
from sqlalchemy.orm import Mapped, mapped_column

from bioc_webstats.database import db


class PackageType(enum.Enum):
    """The major categories for packages as an enum, with enum values as their human-readable forms."""

    BIOC = "bioc"
    EXPERIMENT = "experiment"
    ANNOTATION = "annotation"
    WORKFLOW = "workflow"

def package_type_exists(value: str) -> bool:
    """Is a string a valid PackageType."""
    return value in [e.value for e in PackageType]

def db_valid_thru_date() -> dt.date:
    """The date the database was last upated."""

    # TODO: Stub--get from DB
    return dt.date(2023, 10, 4)

class Stats(db.Model):
    """The table of summary statisttics."""

    category: Mapped[PackageType] = mapped_column(Enum(PackageType), primary_key=True)
    package: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[dt.date] = mapped_column(
        Date,
        primary_key=True,
        comment='Dates repesenting months always have day=1, while years have month=12 and day=31')
    is_monthly: Mapped[bool] = mapped_column(
        Boolean, nullable=False, comment='If true, date span is 1 month, if false, 1 year')
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
    def get_package_names():
        """Return all the package names."""
        return db.session.scalars(
            select(Stats.package)
            .distinct()
            .order_by(Stats.package.asc())).fetchall()

    @staticmethod
    def get_download_counts(category: PackageType,
                            package: Optional[str] = None,
                            year: Optional[int] = None):
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
        if package is not None:
            where_clause.append(Stats.package == package)
        if year is not None:
            where_clause.append(extract('year', Stats.date) == year)
        final_where_clause = and_(*where_clause)

        # Execute query
        result = db.session.scalars(select(Stats)
                                    .where(final_where_clause)
                                    .order_by(asc(Stats.package), asc(Stats.date))
                                    ).fetchall()
        return result

    @staticmethod
    def get_download_scores(category: PackageType,
                            package: Optional[str] = None) -> [(str, int, int)]:
        """Returns download a download score for each package.

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

        x = db_valid_thru_date()
        # the first of the current month
        y = dt.date(x.year, x.month, 1)
        # the last day of the prior month
        end_date = y - relativedelta(days=1)
        # the first day of the date 1 year before the end date
        start_date = y - relativedelta(months=12)

        result = db.session.execute(select(
            Stats.package,
            (func.sum(Stats.ip_count) // 12).label('score'),
            func.rank().over(order_by=func.sum(Stats.ip_count).desc()).label('rank'))
            .where((Stats.category == category) & Stats.date.between(start_date, end_date))
            .group_by(Stats.package)
            .order_by(asc(Stats.package)))
        return result.fetchall()
