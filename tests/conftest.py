import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime


import pytest
from db import DatabaseService, TestDatabaseConnection

@pytest.fixture(scope="module")
def database_access():
    db_service = DatabaseService(TestDatabaseConnection)
    db_service.create()
    yield db_service
    db_service.close()  # Ensure the connection is closed after the test
