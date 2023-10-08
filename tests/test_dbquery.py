import pytest
from unittest.mock import Mock, patch
from dbquery import *

from app.dbquery import *

def test_download_summary_rows_present(database_access):
    # Arrange
    db_service = database_access
    db_service.populate()
    db_service.dump_db()

    # Act
    # Assert

# def test_dbquery_scores():
#     q = DbQueryRequest(query_type=QueryRequestType.PACKAGE_COUNTS, package_type=PackageType.BIOC, package_name='S4Vectors', year='2022')
#     r = dbquery(q)
#     assert r.status == DataRetrievalStatus.SUCCESS
#     assert r.result[0].package_name == 'S4Vectors'

