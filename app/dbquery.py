
import app.dbquery_structures as dbs


def get_db_connection():
    raise NotImplementedError("This function has not yet been implemented.")
    return None




def dbquery(request: dbs.DbQueryRequest) -> dbs.DbQueryResponse:
    """
    Executes a query against the bioc_package_stats database

    Parameters:
    query (db.DbQueryRequest) - The parameters for the query

    Returns:
        db.QueryResponse - The return status code
                If .statusCode is SUCCESS, then the data as well
    Raises:
        TODO: ERROR -- INVALID Query format
    """
    
    # TODO Call dbAdapter
    match request.query_type:
        case dbs.QueryRequestType.PACKAGE_SCORES:
            u = dbs.DbResultEntry(request.package_name, '2021-03-01', False, 1543, 12345)
            r = dbs.DbQueryResponse(status=dbs.DataRetrievalStatus.SUCCESS,
                                    result=[u])
        case dbs.QueryRequestType.PACKAGE_COUNTS:
            # TODO Mean of trailing 12 month ip counts
            u = dbs.DbResultEntry(request.package_name, '2021-03-01', False, 1422, None)
            r = dbs.DbQueryResponse(status=dbs.DataRetrievalStatus.SUCCESS,
                                    result=[u])
            return r
        case dbs.QueryRequestType.PACKAGE_NAMES:
            # TODO THIS IS A STUB
            u = dbs.DbResultEntry(['Bob'], '2021-03-01', False, 1422, None)
            r = dbs.DbQueryResponse(status=dbs.DataRetrievalStatus.SUCCESS,
                                    result=[u])
            return r
        case _:
            raise Exception(f'Invalid request type ({dbs.DbQueryRequest})')

