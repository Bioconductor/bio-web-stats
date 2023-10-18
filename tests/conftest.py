import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
import pandas as pd
from typing import Tuple

import pytest

from db import DatabaseService, DatabaseConnection,  PackageType
from app_helpers import app_config


# This pair of dates is a 1 year span to go with the database test cases
current_date = app_config.today()
test_start_date = date(2022,10,1)
test_end_date =  date(2023,9,30)

database_test_cases = [
    [
        (PackageType.BIOC, 'affydata', '2023-08-01')
    ],
    [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01')
    ],
    [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01'),
        (PackageType.ANNOTATION, 'BSgenome.Hsapiens.UCSC.hg38', '2019-01-01')
    ]
]

# TODO Refactor the database_test_cases: TypeError: list indices must be integers or slices, not tuples 
@pytest.fixture() 
def database_access():
    db_service = DatabaseService(DatabaseConnection)
    db_service.create()
    yield db_service
    
