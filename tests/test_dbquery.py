import pytest
from unittest.mock import Mock, patch

def test_download_summary_rows_present(database_access):
    # Arrange
    sut = database_access
    sut.populate()

    # Act
    result1 = sut.dump_db()
    result2 = sut.execute('select * from download_summary')
    pass

    # Assert
    # dump_db returns the date as date, while execute returns it as str
    assert [(repo, package, str(dt), ip, count) for repo, package, dt, ip, count in result1] == result2
