import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
import pandas as pd
from typing import Tuple

import pytest

from db import PackageType
import db

from app_helpers import app_config



# TODO Refactor the database_test_cases: TypeError: list indices must be integers or slices, not tuples 
@pytest.fixture() 
def database_access():
    # TODO review this
    db.init_db()
    db.create()
    
