import pytest
from unittest.mock import Mock, patch
import sqlite3
from datetime import date, datetime




from app import dbquery


@pytest.fixture()
def mock_get_db_values():
    with patch('app.dbquery.get_db_values', new=Mock(return_value="Your Mocked Value")) as mock_method:
        yield mock_method

@pytest.fixture()
def test_database():
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE download_summary (
    "date" date,
    repo TEXT,
    package TEXT,
    IPcount BIGINT,
    downloadCount BIGINT
    );''')

    def insert_row(date: date, repo: str, package: str, IPcount: int, downloadCount: int):
        cursor.execute("INSERT INTO table_name VALUES (:date, :repo, :package, :IPcount, :downloadCount)",
            {"date":date, "repo":repo, "package":package, "IPcount":IPcount, "downloadCount":downloadCount})

    insert_row(date(2021,7,4), 'bioc', 'S4Vectors', 123, 23423)
    
    cursor.execute("SELECT * FROM download_summary;")
    rows = cursor.fetchall()

    print(rows)

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM download_summary")
    rows = cursor.fetchall()

    rows_as_dict = [dict(row) for row in rows]
    print(rows_as_dict)
    pass