from sqlalchemy import Engine, Connection, MetaData
from sqlalchemy import Table, Column, BigInteger, String, Date
from sqlalchemy import create_engine, select, insert, text
from sqlalchemy.exc import SQLAlchemyError

from typing import List, Tuple

from datetime import date, datetime
from random import randint

# TODO HACK BELOW MERGE WITH dbquery.py
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
    
class TestDatabaseConnection(DatabaseConnectionInterface):
    # TODO echo=True ==> this is a trace parameter.
    _engine: Engine = None
    _connection: Connection = None

    @staticmethod
    def engine() -> Engine:
        if TestDatabaseConnection._engine is None:
            TestDatabaseConnection._engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
        return TestDatabaseConnection._engine

    @staticmethod
    def connection() -> Connection:
        return TestDatabaseConnection.engine().connect()
    
    @staticmethod
    def close_connection():
        if TestDatabaseConnection._connection:
            TestDatabaseConnection._connection.close()
            TestDatabaseConnection._connection = None

class DatabaseService:
    '''
    TODO: refactor after real db is up
    '''
    db: DatabaseConnectionInterface
    download_summary: Table
    
    def __init__(self, db: DatabaseConnectionInterface):
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

    def populate(self):
        start_date = date(2022, 12, 1)
        end_date = date(2023, 9, 1)

        dates_list = [date(year, month, 1) 
                    for year in range(start_date.year, end_date.year + 1) 
                    for month in range(1, 13) 
                    if date(year, month, 1) >= start_date and date(year, month, 1) <= end_date]
        # HACK
        for repo in [x.value for x in PackageType]:
            for pkg in [f'pkg{repo}{i}' for i in range(1, 2)]:
                for d in dates_list:
                    self.download_count_insert([(repo, pkg, d, randint(1, 10000), randint(1, 10000))])

    def download_count_insert(self, rows: List[Tuple]) -> None:
        with self.db.connection() as conn:
            conn.execute(insert(self.download_summary).values(rows))
            conn.commit()

    def dump_db(self):
        with self.db.connection() as conn:
            result = conn.execute(select(self.download_summary))
            conn.commit()
            for row in result:
                print(row)

# service = DatabaseService(TestDatabaseConnection())
# service.create()
# service.populate()
# service.dump_db()

 

