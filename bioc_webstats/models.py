# -*- coding: utf-8 -*-
"""Stats models."""

import datetime as dt
import enum
from typing import Optional

from sqlalchemy import BigInteger, Date, Enum, String, and_, asc, extract, select, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from bioc_webstats.database import db


class PackageType(enum.Enum):
    """_summary_.

    Arguments:
        enum -- _description_
    """

    BIOC = "bioc"
    EXPERIMENT = "experiment"
    ANNOTATION = "annotation"
    WORKFLOW = "workflow"

def package_type_exists(value: str) -> bool:
    """Is a string a valid PackageType."""
    return value in [e.value for e in PackageType]

class Stats(db.Model):
    """The table of summary statisttics."""

    category: Mapped[PackageType] = mapped_column(Enum(PackageType), primary_key=True)
    package: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[dt.date] = mapped_column(Date, primary_key=True, comment='Dates repesenting months always have day=1, while years have month=12 and day=31')
    is_monthly: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='If true, date span is 1 month, if false, 1 year')
    ip_count: Mapped[int] = mapped_column(BigInteger, nullable=False)
    download_count: Mapped[int] = mapped_column(BigInteger, nullable=False)

    from sqlalchemy.ext.declarative import declarative_base

    def __repr__(self):
        """_summary_.

        Returns:
            _description_
        """
        return f"Stats(category={self.category}, package='{self.package}', date='{self.date}', ip_count={self.ip_count}, download_count={self.download_count})"
         
    
    @staticmethod
    def get_package_names():
        """Return all the package names."""
        return db.session.scalars(select(Stats.package)
                                  .distinct()
                                  .order_by(Stats.package.asc())
                                  ).fetchall()

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
                            package: Optional[str] = None,
                            year: Optional[int] = None):
        # TODO JUST FAKIING IT WITH COUNTS...DO THE WORK
        return Stats.get_download_counts(category, package, year)
