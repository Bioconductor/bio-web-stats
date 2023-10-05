from flask import Flask, Response
import dbquery_structures as dbs
from dbquery import dbquery

# TODO for initial test only
app = Flask(__name__)

# TODO How to express the URL prefix?
@app.route('/packages/stats/bioc/bioc_packages.txt', methods=['GET'])
def index():


    query_request = dbs.DbQueryRequest(query_type=dbs.QueryRequestType. 
                                       PACKAGE_SCORES,package_type=None,package_name=None,year=None)

    query_response = dbquery(query_request)

    match query_response.status:

        case dbs.DataRetrievalStatus.SUCCESS:
            return Response(query_response.result, content_type="text/plain")
        case dbs.DataRetrievalStatus.TIMEOUT:
            return Response(status=429)
        case _:
           return Response(status=500)

        
   

if __name__ == '__main__':
    app.run(debug=True)
