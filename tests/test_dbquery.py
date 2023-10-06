from dbquery import *

def test_dbquery_scores():
    q = DbQueryRequest(query_type=QueryRequestType.PACKAGE_COUNTS, package_type=PackageType.BIOC, package_name='S4Vectors', year='2022')
    r = dbquery(q)
    assert r.status == DataRetrievalStatus.SUCCESS
    assert r.result[0].package_name == 'S4Vectors'

    