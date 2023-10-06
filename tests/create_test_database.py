import sqlite3
from datetime import date, datetime
import random
from dbquery import *


def create_test_database(connection: sqlite3.Connection):
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE download_summary (
    "date" date,
    repo TEXT,
    package TEXT,
    IPcount BIGINT,
    downloadCount BIGINT
    );''')

    def insert_row(date: date, repo: str, package: str, IPcount: int, downloadCount: int):
        cursor.execute("INSERT INTO download_summary VALUES (:date, :repo, :package, :IPcount, :downloadCount)",
            {"date":date, "repo":repo, "package":package, "IPcount":IPcount, "downloadCount":downloadCount})

    start_date = date(2022, 1, 1)
    end_date = date(2023, 9, 1)

    dates_list = [date(year, month, 1) 
                for year in range(start_date.year, end_date.year + 1) 
                for month in range(1, 13) 
                if date(year, month, 1) >= start_date and date(year, month, 1) <= end_date]

    for repo in PackageType:
        for pkg in [f'pkg{repo}{i}' for i in range(1, 4)]:
            for d in dates_list:
                insert_row(d, repo.value, pkg, random.randint(1, 10000), random.randint(1, 10000))

