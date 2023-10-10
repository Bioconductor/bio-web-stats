import pytest
from unittest.mock import Mock, patch
from datetime import date
from db.db import PackageType
import pandas as pd
import app.dbquery as queries


database_test_cases = [
    [
        ('bioc', 'affydata', '2023-08-01')
    ],
    [
        ('bioc', 'affy', '2023-09-01'), 
        ('bioc', 'affydata', '2023-08-01')
    ]
]

@pytest.mark.parametrize("test_case", database_test_cases)
def test_populate_database_one_package(test_case, database_access):
    # Arrange
    sut = database_access
    expected = sut.populate(123, date(2023, 10, 1), test_case)
    
    # Act
    result = sut.select()
    pass

    # Assert
    assert result.equals(expected)
    
@pytest.mark.parametrize("test_case", database_test_cases)
def test_get_package_names(test_case, database_access):
    # Arrange
    sut = database_access
    df = sut.populate(123, date(2023, 10, 1), test_case)
    expected = df[['package']].drop_duplicates()

    # Act
    result = sut.get_package_names()

    # Assert
    assert set(result.package) == set(expected.package)

