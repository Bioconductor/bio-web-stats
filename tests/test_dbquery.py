import pytest
from unittest.mock import Mock, patch
from datetime import date
from db.db import PackageType
import pandas as pd

def test_populate_database_one_package(database_access):
    # Arrange
    sut = database_access
    expected_data = [('bioc', 'affy', '2023-09-01', 858, 35085), 
                ('bioc', 'affy', '2023-10-01', 1429, 53378)]
    columns = ['repo', 'package', 'date', 'ip_count', 'download_count']

    expected = pd.DataFrame(expected_data, columns=columns)


    sut.populate(123, date(2023, 10, 1), [(PackageType.BIOC.value, 'affy', date(2023, 9, 1))])

    # Act
    result = sut.execute('select repo, package, "date", ip_count, download_count from download_summary')
    pass

    # Assert
    assert result.equals(expected)