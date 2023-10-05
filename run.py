from flask import Flask, Response
import app.dbquery_structures as dbs
from app.dbquery import dbquery

# TODO for initial test only
app = Flask(__name__)

# TODO How to express the URL prefix?
@app.route('/packages/stats/bioc/bioc_packages.txt', methods=['GET'])
def get_packages():

    query_request = dbs.DbQueryRequest(query_type=dbs.QueryRequestType. 
                                       PACKAGE_NAMES,package_type=None,package_name=None,year=None)

    query_response = dbquery(query_request)

    match query_response.status:

        case dbs.DataRetrievalStatus.SUCCESS:
            return Response(query_response.result, content_type="text/plain")
        case dbs.DataRetrievalStatus.TIMEOUT:
            return Response(status=429)
        case _:
           return Response(status=500)

#bioc/bioc_pkg_scores.tab
@app.route('/packages/stats/bioc/bioc_pkg_scores.tab', methods=['GET'])
def get_pakages_scores():

    query_request = dbs.DbQueryRequest(query_type=dbs.QueryRequestType.PACKAGE_SCORES,package_type=None,package_name=None,year=None)
    query_response = dbquery(query_request)

    match query_response.status:

        case dbs.DataRetrievalStatus.SUCCESS:
            return Response(query_response.result, content_type="text/tab-separated-values")
        case dbs.DataRetrievalStatus.TIMEOUT:
            return Response(status=429)
        case _:
           return Response(status=500)


#bioc/bioc_pkg_stats.tab
# @app.route('/packages/stats/bioc/bioc_pkg_stats.tab', methods=['GET'])


# #bioc/S4Vectors/
# @app.route('/packages/stats/bioc/S4Vectors/', methods=['GET'])


# #bioc/S4Vectors/S4Vectors_2023_stats.tab
# @app.route('/packages/stats/bioc/S4Vectors/S4Vectors_2023_stats.tab', methods=['GET'])


# #bioc/S4Vectors/S4Vectors_stats.tab 
# @app.route('/packages/stats/bioc/S4Vectors/S4Vectors_stats.tab', methods=['GET'])


# #ROOT
# @app.route('/packages/stats/', methods=['GET'])


# #BIOC
# @app.route('/packages/stats/bioc', methods=['GET'])





   

if __name__ == '__main__':
    app.run(debug=True)
