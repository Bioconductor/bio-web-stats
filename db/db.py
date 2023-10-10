
from sqlalchemy import Engine, Connection, MetaData
from sqlalchemy import Table, Column, BigInteger, String, Date
from sqlalchemy import create_engine, select, insert, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd

from typing import List, Tuple
from collections import namedtuple

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import seed, randint

from enum import Enum

class PackageType(Enum):
    BIOC = "bioc"
    EXPERIMENT = "experiment"
    ANNOTATION = "annotation"
    WORKFLOW = "workflow"

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
            TestDatabaseConnection._engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
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
            Column("repo", String, primary_key=True),
            Column("package", String, primary_key=True),
            Column("date", Date, primary_key=True),
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
                
        df = [(repo, package, d, randint(1, 10000), randint(1, 100000)) for repo, package, start_date in packages
            for d in months_sequence(datetime.strptime(start_date, '%Y-%m-%d').date(), end_date)]

        self.download_count_insert(df)
        
        return pd.DataFrame(df, columns=['repo', 'package', 'date', 'ip_count', 'download_count'])

    def download_count_insert(self, rows: List[Tuple]) -> None:
        with self.db.connection() as conn:
            conn.execute(insert(self.download_summary).values(rows))
            conn.commit()

    def dump_db(self) -> [tuple]:
        with self.db.connection() as conn:
            result = conn.execute(select(self.download_summary))
            conn.commit()
            tuple_list = [tuple(row) for row in result]
            return tuple_list

    def select(self) -> pd.DataFrame:
        with self.db.connection() as conn:
            result = conn.execute(select(self.download_summary))
            conn.commit()
            return pd.DataFrame(result.fetchall(), columns=result.keys())
        
    def execute(self, statement: str) -> pd.DataFrame:
        with self.db.connection() as conn:
            result = conn.execute(text(statement))
            conn.commit()
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    
    # Methods below this point should be an a facade tier e.g. in the app
    def get_package_names(self) -> pd.DataFrame:
        with self.db.connection() as conn:
            result = conn.execute(text('select distinct package from download_summary order by package'))
            conn.commit()
            return pd.DataFrame(result.fetchall(), columns=result.keys())
        return result

        
    
