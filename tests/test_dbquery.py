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


def test_populate_database_one_package(database_access):
    # Arrange
    sut = database_access
    sut.populate(123, date(2023, 10, 1), database_test_cases[0])
    expected = sut.select()

    # Act
    result = sut.select()
    pass

    # Assert
    assert result.equals(expected)
    
# def test_get_package_names(database_access):
#     # Arrange
#     sut, source_data = database_access
#     expected_data = [('affy')]
#     columns = ['package']
#     expected = pd.DataFrame(expected_data, columns=columns)
#     sut.populate(123, date(2023, 10, 1), [(PackageType.BIOC.value, 'affy', date(2023, 9, 1))])

#     # Act
#     result = sut.get_package_names()
#     pass

#     # Assert
#     assert result.equals(expected)

