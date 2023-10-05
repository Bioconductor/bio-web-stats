'''
conftest.py - shareable fixtures
'''

import pytest
from unittest.mock import patch

import sqlite3

import app.dbquery 
import app.dbquery_structures as dbs


@pytest.fixture
def mock_db_connection():
    with patch('app.dbquery.get_db_connection') as mock_connection:
        mock_connection.return_value = None
        yield

 # test_sample.py
def test_some_db_function(mock_db_connection):
    # Your test code here. All calls to `get_db_connection` within this test will return None.
    assert mock_db_connection == None