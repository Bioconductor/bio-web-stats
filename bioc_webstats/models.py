"""Stats models."""

import datetime as dt
import enum
from typing import List, Optional

import pandas as pd

from dateutil.relativedelta import relativedelta
from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    Enum,
    Integer,
    String,
    and_,
    asc,
    desc,
    extract,
    func,
    insert,
    select,
    text,
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


def list_to_dict(u) -> List[dict]:
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
        ).first()
        return dt.datetime.strptime(x, "%Y-%m-%d").date()


class Packages(Model):
    """All Package Names from git.bioconductor.org."""

    package: Mapped[str] = mapped_column(String, primary_key=True)
    category: Mapped[str] = mapped_column(String)
    first_version: Mapped[str] = mapped_column(String)
    last_version: Mapped[str] = mapped_column(String)
    
    @staticmethod
    def get_package_names():
        """Return all the package names."""
        return db.session.scalars(
            select(Packages.package).order_by(Packages.package.asc())
        ).fetchall()
        
    @staticmethod
    def get_package_details(package: str):
        """Return the summary information about a specific pacakge."""
        return db.session.execute(
            select(Packages.package, 
                Packages.category, 
                Packages.first_version, 
                Packages.last_version).
            where(Packages.package == package)
        ).fetchone()
        


class Categorystats(Model):
    """This is a projection of Stats with the package column removed."""

    category: Mapped[PackageType] = mapped_column(Enum(PackageType), primary_key=True)
    date: Mapped[dt.date] = mapped_column(
        Date,
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
            f"Categorystats(category={self.category}, "
            f"date='{self.date}', ip_count={self.ip_count}, "
            f"download_count={self.download_count})"
        )

    # because distinct IP's is over the category
    @staticmethod
    def get_combined_counts(category: PackageType, year: Optional[int] = None):
        """Get counts combined for all packages in a given category.

        Arguments:
            category -- The category

        Returns:
            _description_
        """
        where_clause = [Categorystats.category == category.value]
        if year is not None:
            where_clause.append(extract("year", Categorystats.date) == year)

        result = db.session.execute(
            select(
                Categorystats.date,
                Categorystats.ip_count,
                Categorystats.download_count,
            )
            .where(and_(*where_clause))
            .order_by(desc(extract("year", Categorystats.date)), asc(Categorystats.date))
        )

        return result.fetchall()


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
        category: PackageType,
        package: Optional[str] = None,
        year: Optional[int] = None,
        newest_year_first: Optional[bool] = True,
    ):
        """_summary_.

        Arguments:
            category -- _description_

        Keyword Arguments:
            package -- _description_ (default: {None})
            year -- _description_ (default: {None})
            newest_year_first -- If True, rows are logically grouped by year in descending order
                if False, rows are strictly in date order (default: True)

        Returns:
            _description_
        """
        where_clause = [Stats.category == category.value]
        select_clause = [Stats.date, Stats.ip_count, Stats.download_count]
        order_clause = [asc(Stats.date)]

        if package is not None:
            where_clause.append(Stats.package == package)
        else:
            select_clause = [Stats.package] + select_clause
        if year is not None:
            where_clause.append(extract("year", Stats.date) == year)
        if newest_year_first:
            order_clause = [desc(extract("year", Stats.date))] + order_clause

        final_where_clause = and_(*where_clause)

        # Execute query
        text = (
            select(*select_clause)
            .where(final_where_clause)
            .order_by(asc(Stats.package), *order_clause)
        )

        result = db.session.execute(text).fetchall()
        return result

    @staticmethod
    def get_download_scores(category: PackageType):  # TODO was -> (str, int, int):
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

        query = (select(
                Stats.package,
                (func.sum(Stats.ip_count) // 12).label("score"),
                func.rank()
                .over(order_by=func.sum(Stats.ip_count).desc())
                .label("rank"),
            )
            .where(
                and_(
                    Stats.category == category.value,
                    Stats.date.between(start_date, end_date),
                    Stats.is_monthly == True # noqa E712 -- causes and_ to malfunction
                )
            )
            .group_by(Stats.package)
            .order_by(asc(Stats.package))
        )

        result = db.session.execute(query)
        return result.fetchall()


class    BiocWebDownloads(Model):
    """Source records for downloads table bioc_web_downloads"""

    __tablename__ = 'bioc_web_downloads'
    date: Mapped[str] = mapped_column(
        Date, primary_key=True
    )
    c_ip: Mapped[str] = mapped_column(
        'c-ip', String(40)
    )
    sc_status: Mapped[int] = mapped_column(
        'sc-status',
        Integer
    )
    category: Mapped[str] = mapped_column(
        'category',
        String(16)
    )
    package: Mapped[str] = mapped_column(
        'package',
        String(64)
    )
    
    @staticmethod
    def insert_from_dataframe(dataframe: pd.DataFrame):
        """Move a dataframe of download records to web_bioc_download

        Arguments:
            dataframe -- A pandas dataframe that matches the format of this class
        """

        db.session.execute(insert(BiocWebDownloads), dataframe.to_dict(orient='records'))
        db.session.commit()

    @staticmethod
    def update_stats_from_downloads(start_date: Date):
        chr_date = start_date.strftime('%Y-%m-%d')
        # TODO verify sproc distribution
        db.session.execute(text(f"CALL public.update_stats(DATE '{chr_date}');"))

    def __repr__(self):
        return f"<BiocWebDownloads(date={self.date}, c_ip={self.c_ip}, sc_status={self.sc_status}, category={self.category}, package={self.package})>"
