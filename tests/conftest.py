import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
import pandas as pd
from typing import Tuple

import pytest
from db.db import DatabaseService, TestDatabaseConnection


# TODO Refactor the database_test_cases: TypeError: list indices must be integers or slices, not tuples 
@pytest.fixture() 
def database_access():
    db_service = DatabaseService(TestDatabaseConnection)
    db_service.create()
    yield db_service
    
