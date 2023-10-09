import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime


import pytest
from db.db import DatabaseService, TestDatabaseConnection

@pytest.fixture(scope="module")
def database_access():
    db_service = DatabaseService(TestDatabaseConnection)
    db_service.create()
    yield db_service
