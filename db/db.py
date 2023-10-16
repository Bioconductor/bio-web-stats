
from sqlalchemy import CursorResult, Engine, Connection, MetaData, asc, desc, extract
from sqlalchemy import Table, Column, BigInteger, String, Date
from sqlalchemy import create_engine, select, insert, Enum as SQLEnum
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import Optional

from enum import Enum
from typing import Any, List, Tuple
from collections import namedtuple

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import seed, randint

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
            TestDatabaseConnection._engine  = create_engine('sqlite:////tmp/test.db')
        return TestDatabaseConnection._engine

    @staticmethod
    def connection() -> Connection:
        return TestDatabaseConnection.engine().connect()
        
class DatabaseService:
    '''
    TODO: refactor after real db is up
    '''
    db: DatabaseConnectionInterface
    download_summary: Table
    
    def __init__(self, db: DatabaseConnectionInterface) -> None:
        self.db = db
        
    def create(self):
        metadata = MetaData()
        self.download_summary = Table("download_summary", 
            metadata,
            Column("category", SQLEnum(PackageType), nullable=False, primary_key=True),
            Column("package", String, nullable=False, primary_key=True),
            Column("date", Date, nullable=False, primary_key=True),
            Column("ip_count", BigInteger),
            Column("download_count", BigInteger)
        )
        metadata.create_all(self.db.engine())
        

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
                
        df = [(category, package, d, randint(1, 10000), randint(1, 100000)) for category, package, start_date in packages
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
        
        # TODO lambda to make it more clear
    def get_download_scores(self, category: PackageType, 
                            package: Optional[str] = None):
        # TODO THIS IS A STUB
        return pd.DataFrame()

        
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
