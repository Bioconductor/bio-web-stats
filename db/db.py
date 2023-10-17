
from sqlalchemy import CursorResult, Engine, Connection, MetaData, asc, desc, extract
from sqlalchemy import Table, Column, BigInteger, String, Date
from sqlalchemy import create_engine, select, insert, Enum as SQLEnum, bindparam, text, func
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import Optional
from app.app_helpers import app_config

from enum import Enum
from typing import Any, List, Tuple
from collections import namedtuple

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import seed, randint

import app.app_helpers as ah

def cursor_to_dataframe(cursor: CursorResult[Any]) -> pd.DataFrame:
    return pd.DataFrame(cursor.fetchall(), columns=cursor.keys())

class PackageType(Enum):
    BIOC = "bioc"
    EXPERIMENT = "experiment"
    ANNOTATION = "annotation"
    WORKFLOW = "workflow"
    
def packge_type_exists(value: str) -> bool:
    """
	Is a string a valid PackageType
    """
    return value in [e.value for e in PackageType]


class DatabaseConnectionInterface:
    def engine() -> Engine:
        raise NotImplementedError
    
    def connection() -> Connection:
        raise NotImplementedError
    
    def close() -> None:
        raise NotImplementedError
    

class TestDatabaseConnection(DatabaseConnectionInterface):
    # TODO echo=True ==> this is a trace parameter.
    _engine: Engine = None

    @staticmethod
    def engine() -> Engine:
        if TestDatabaseConnection._engine is None:
            # TestDatabaseConnection._engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
            TestDatabaseConnection._engine  = create_engine('sqlite:////tmp/test.db', echo=True)
        return TestDatabaseConnection._engine

    @staticmethod
    def connection() -> Connection:
        return TestDatabaseConnection.engine().connect()

# TODO: Error handling.
class DatabaseService:
    '''
    TODO: refactor after real db is up
    '''
    db: DatabaseConnectionInterface
    download_summary: Table

    def __init__(self, db: DatabaseConnectionInterface) -> None:
        self.db = db
        self.download_summary = self.create()  # Initialize the table during initialization

    def create(self):
        metadata = MetaData()
        download_summary = Table("download_summary",
            metadata,
            Column("category", SQLEnum(PackageType), nullable=False, primary_key=True),
            Column("package", String, nullable=False, primary_key=True),
            Column("date", Date, nullable=False, primary_key=True),
            Column("ip_count", BigInteger),
            Column("download_count", BigInteger)
        )
        metadata.create_all(self.db.engine())
        return download_summary
        

    # TODO Replace randint with hash on all keys for better validation
    def populate(self, seed_value: int, end_date: date, packages: [tuple]) -> pd.DataFrame:
        
        # clear all previous entries
        with self.db.connection() as conn:
            conn.execute(self.download_summary.delete())
            conn.commit()

        seed(seed_value)
        def months_sequence(start_date: date, end_date: date):
            """Yield the first day of each month from start_date to end_date inclusive."""
            current_date = start_date
            
            while current_date <= end_date:
                yield current_date
                current_date += relativedelta(months=1)
                
        df = [(category, package, d, randint(1, 10000) + 0, randint(1, 100000) + 0) for category, package, start_date in packages
            for d in months_sequence(datetime.strptime(start_date, '%Y-%m-%d').date(), end_date)]
        
        self.download_count_insert(df)
        return pd.DataFrame(df, columns=['category', 'package', 'date', 'ip_count', 'download_count'])

    def download_count_insert(self, rows: List[Tuple]) -> None:
        with self.db.connection() as conn:
            conn.execute(insert(self.download_summary).values(rows))
            conn.commit()

    def select(self) -> pd.DataFrame:
        with self.db.connection() as conn:
            result = conn.execute(select(self.download_summary))
            conn.commit()
            return cursor_to_dataframe(result)
        
    # Methods below this point should be an a facade tier e.g. in the app
    
    def get_package_names(self) -> pd.DataFrame:
        with self.db.connection() as conn:
            result = conn.execute(
                select(self.download_summary.c.package.distinct())
                    .order_by(self.download_summary.c.package)
                )
            conn.commit()
            return cursor_to_dataframe(result)
    
    # TODO can combine with 'for_catagory with lambda function for where
    def get_download_score_for_package(self, package: str) -> pd.DataFrame:
        
        x = app_config.today()
        # the first of the current month
        y = date(x.year, x.month, 1)
        # the last day of the prior month
        end_date = y - relativedelta(days=1)
        # the first day of the date 1 year before the end date
        start_date = y - relativedelta(months=12)
        with self.db.connection() as conn:
            result = conn.execute(select(self.download_summary.c.package, 
                        (func.sum(self.download_summary.c.ip_count) // 12).label('score'))
                    .where((self.download_summary.c.package == package)
                        & self.download_summary.c.date.between(start_date, end_date))
                    .group_by(self.download_summary.c.package)
                    .order_by(asc(self.download_summary.c.package), asc(self.download_summary.c.date))
                    )
        df = cursor_to_dataframe(result)
        return df

    def get_download_scores_for_category(self, category: PackageType) -> pd.DataFrame:
        """Computes an activity score and a rank for each package the given category.
        
        See get_download_scores_for_package for the calculation of score
        The rank is an ordinal that indicates relative activity.
        Rank = 1 is the most downloaded package in the category, Raank=2 is next, etc.

        Arguments:
            category -- The PackageType for the category to score

        Returns:
            DataFrame with columsn (package, score, rank)
        """
        x = app_config.today()
        # the first of the current month
        y = date(x.year, x.month, 1)
        # the last day of the prior month
        end_date = y - relativedelta(days=1)
        # the first day of the date 1 year before the end date
        start_date = y - relativedelta(months=12)
        with self.db.connection() as conn:
                result = conn.execute(select(self.download_summary.c.package, 
                            (func.sum(self.download_summary.c.ip_count)// 12).label('score'),
                            func.rank().over(order_by=func.sum(self.download_summary.c.ip_count).desc()).label('rank')

                        )
                    .where((self.download_summary.c.category == category)
                        & self.download_summary.c.date.between(start_date, end_date))
                    .group_by(self.download_summary.c.package)
                    .order_by(asc(self.download_summary.c.package))
                    )
        result = cursor_to_dataframe(result)
        return result

        
    # TODO lambda to make it more clear
    def get_download_counts(self, category: PackageType, 
                            package: Optional[str] = None, 
                            year: Optional[int] = None):
        with self.db.connection() as conn:
            if package is None:
                result = conn.execute(select(self.download_summary)
                        .where((self.download_summary.c.category == category))
                        .order_by(asc(self.download_summary.c.package), asc(self.download_summary.c.date))
                    )
            elif year is None:
                result = conn.execute(select(self.download_summary)
                        .where((self.download_summary.c.category == category) 
                            & (self.download_summary.c.package == package))
                        .order_by(asc(self.download_summary.c.package), asc(self.download_summary.c.date))
                    )
            else:
                result = conn.execute(select(self.download_summary)
                        .where((self.download_summary.c.category == category) 
                            & (self.download_summary.c.package == package)
                            & (extract('year',self.download_summary.c.date) == year))
                        .order_by(asc(self.download_summary.c.package), asc(self.download_summary.c.date))
                    )
            conn.commit()
            return cursor_to_dataframe(result)
