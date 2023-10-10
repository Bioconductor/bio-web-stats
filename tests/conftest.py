import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
import pandas as pd
from typing import Tuple

import pytest
from db.db import DatabaseService, TestDatabaseConnection


database_test_cases = [
    [
        ('bioc', 'affydata', '2023-08-01')
    ],
    [
        ('bioc', 'affy', '2023-09-01'), 
        ('bioc', 'affydata', '2023-08-01')
    ]
]

# TODO Refactor the database_test_cases: TypeError: list indices must be integers or slices, not tuples 
@pytest.fixture(params=database_test_cases) 
def database_access(request):
    db_service = DatabaseService(TestDatabaseConnection)
    db_service.create()
    
    # columns = ['repo', 'package', 'date', 'ip_count', 'download_count']
    # pd_data = pd.DataFrame(request.param , columns=columns)
    
    db_service.populate(123, date(2023, 10, 1), request.param)
    pd_data = db_service.select()
    yield db_service, pd_data
