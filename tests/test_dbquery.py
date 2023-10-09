import pytest
from unittest.mock import Mock, patch
from datetime import date

def test_populate_database_one_package(database_access):
    # Arrange
    sut = database_access
    expected = [('bioc', 'affy', '2023-09-01', 858, 35085), 
                ('bioc', 'affy', '2023-10-01', 1429, 53378)]
    
    sut.populate(123, date(2023, 10, 1), [('bioc', 'affy', date(2023, 9, 1))])

    # Act
    result = sut.execute('select repo, package, "date", ip_count, download_count from download_summary')
    pass

    # Assert
    assert result == expected