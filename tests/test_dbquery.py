import pytest
from unittest.mock import Mock, patch
from app import dbquery

from app.dbquery import *

@pytest.fixture()
def mock_get_db_values():
    with patch('app.dbquery.get_db_values', new=Mock(return_value="Your Mocked Value")) as mock_method:
        yield mock_method

def test_dbquery_scores():
    q = DbQueryRequest(query_type=QueryRequestType.PACKAGE_COUNTS, package_type=PackageType.BIOC, package_name='S4Vectors', year='2022')
    r = dbquery(q)
    assert r.status == DataRetrievalStatus.SUCCESS
    assert r.result[0].package_name == 'S4Vectors'

def test_example(mock_get_db_values):
    # Your test code here.
    
    mock_get_db_values.assert_called_once_with("Your Expected Input")
