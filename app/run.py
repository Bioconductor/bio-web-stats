from flask import Flask, make_response, Response, abort
from flask_sqlalchemy import SQLAlchemy

from markupsafe import escape
import db.db as db
from dbquery import *
#### CAUTION: WORK-IN-PROGRESS...NON-FUNCTIONAL AT 11-OCT-2023 9:23 AM
# TODO for initial test only
app = Flask(__name__)
# TODO For mock-up test only FROM HERE VVVVV
test_database_spec = [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01'),
        (PackageType.ANNOTATION, 'BSgenome.Hsapiens.UCSC.hg38', '2019-01-01')
    ]
from datetime import date
with app.app_context():
    db_service = db.DatabaseService(db.TestDatabaseConnection)
    db_service.create()
    db_service.populate(123, date(2023, 10, 1), test_database_spec)
# TO HERE ^^^^^^^^^^^^^^^^^

# TODO How to express the URL prefix?
@app.route('/packages/stats/bioc/bioc_packages.txt', methods=['GET'])
def get_packages():
    
    payload = db_service.get_package_names()
    response = ('\n').join([row for row in payload['package']])
    return response
            

# #bioc/bioc_pkg_scores.tab
# @app.route('/packages/stats/<package_type>/<package_type_2>_pkg_scores.tab', methods=['GET'])
# def get_pakages_scores(package_type, package_type_2):
#     if  escape(package_type) != escape(package_type_2) or not packge_type_exists(package_type):
#         return Response(status=404)
    
#     query_request = DbQueryRequest(query_type=QueryRequestType.PACKAGE_SCORES,package_type=package_type,package_name=None,year=None)
#     query_response = dbquery(query_request)

#     match query_response.status:

#         case DataRetrievalStatus.SUCCESS:
#             return Response(query_response.result, content_type="text/plain")
#         case DataRetrievalStatus.TIMEOUT:
#             return Response(status=429)
#         case _:
#            return Response(status=500)


# #bioc/bioc_pkg_stats.tab
# @app.route('/packages/stats/<package_type>/<package_type_2>_pkg_stats.tab', methods=['GET'])
# def get_packages_stats(package_type, package_type_2):
#     if  escape(package_type) != escape(package_type_2) or not packge_type_exists(package_type):
#         return Response(status=404)
    
#     query_request = DbQueryRequest(query_type=QueryRequestType.PACKAGE_COUNTS,package_type=package_type,package_name=None,year=None)
#     query_response = dbquery(query_request)

#     match query_response.status:

#         case DataRetrievalStatus.SUCCESS:
#             return Response(query_response.result, content_type="text/plain")
#         case DataRetrievalStatus.TIMEOUT:
#             return Response(status=429)
#         case _:
#            return Response(status=500)


# # #bioc/S4Vectors/S4Vectors_2023_stats.tab
# @app.route('/packages/stats/<package_type>/<package_name>/<package_name_2>_<package_year>_stats.tab', methods=['GET'])
# def get_existing_packages_stats_year(package_type,package_name, package_name_2, package_year):
#     # validation : can we keep it simple ? 4 params need lot of validation checks
#     # if (correct path) 
#     #   query()
#     # else
#     #   status=404

#     if not packge_type_exists(package_type):
#         return Response(status=404)
    
#     if package_name != package_name_2:
#         return Response(status=404)
    
#     query_request = DbQueryRequest(query_type=QueryRequestType.PACKAGE_COUNTS,package_type=package_type,package_name=package_name,year=package_year)
#     query_response = dbquery(query_request)

#     match query_response.status:

#         case DataRetrievalStatus.SUCCESS:
#             return Response(query_response.result, content_type="text/plain")
#         case DataRetrievalStatus.TIMEOUT:
#             return Response(status=429)
#         case _:
#            return Response(status=500)

# # #bioc/S4Vectors/S4Vectors_stats.tab 
# @app.route('/packages/stats/<package_type>/<package_name>/<package_name_2>_stats.tab', methods=['GET'])
# def get_existing_package_stats(package_type,package_name,package_name_2):
    
#     if not packge_type_exists(package_type):
#         return Response(status=404)
    
#     if package_name != package_name_2:
#         return Response(status=404)
    
#     query_request = DbQueryRequest(query_type=QueryRequestType.PACKAGE_SCORES,package_type=package_type,package_name=package_name,year=None)
#     query_response = dbquery(query_request)

#     match query_response.status:

#         case DataRetrievalStatus.SUCCESS:
#             return Response(query_response.result, content_type="text/plain")
#         case DataRetrievalStatus.TIMEOUT:
#             return Response(status=429)
#         case _:
#            return Response(status=500)
    


# #bioc/S4Vectors/
# @app.route('/packages/stats/<package_type>/<package_name>/', methods=['GET'])
# def get_exixsting_package(package_type, package_name):
#     



# #ROOT
# @app.route('/packages/stats/', methods=['GET'])


# #BIOC
# @app.route('/packages/stats/bioc', methods=['GET'])
