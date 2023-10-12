from flask import Flask, make_response, Response, abort
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import pandas as pd

import db.db as dbm
from db.db import PackageType, packge_type_exists

PATH = '/packages/stats'

# TDODO: THIS IS MOCK DATABASE FOR INITIAL TESTING
from datetime import date

test_database_spec = [
        (PackageType.BIOC, 'affy', '2023-09-01'), 
        (PackageType.BIOC, 'affydata', '2023-08-01'),
        (PackageType.ANNOTATION, 'BSgenome.Hsapiens.UCSC.hg38', '2019-01-01')
    ]

db = dbm.DatabaseService(dbm.TestDatabaseConnection)
db.create()
db.populate(123, date(2023, 10, 1), test_database_spec)

app = Flask(__name__)

@app.route(PATH + '/bioc/bioc_packages.txt', methods=['GET'])
def show_packages():    
    payload = db.get_package_names()
    text = ('\n').join([row for row in payload['package']])
    return Response(text, content_type='text/plain')

# #bioc/bioc_pkg_scores.tab and package_stats.tab
@app.route(PATH + '/<package_type>/<package_type_in_filenames>_pkg_<scores_or_stats>.tab', methods=['GET'])
def show_pakages_scores(package_type, package_type_in_filenames, scores_or_stats):
    # We match the legacy system, where both the path and the file_name included the category
    if  escape(package_type) != escape(package_type_in_filenames) or not packge_type_exists(package_type):
        abort(404)
    match scores_or_stats:
        case 'scores':
            raise NotImplementedError
        case 'stats':
            payload = db.get_download_counts(PackageType(package_type))
        case '_':
            abort(404)
    text = dataframe_to_text_tab(payload)
    text = ('\n').join([row for row in text])
    return Response(text, content_type='text/plain')


#TODO - More work needed - the supervening code is in format_helpers.py and still needs work
def df_enum_columns_to_values(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        # Check if any entry in the column is an instance of PackageType
        if any(isinstance(value, PackageType) for value in df[column]):
            df[column] = [e.value for e in df[column]]
    return df

# TODO These utility fuctions should be moved to a more appropriate location
def dataframe_to_string_list(df: pd.DataFrame) ->[str]:
    headers = list(df.columns)
    header_string = "\t".join(headers)
    rows = [header_string]
    for _, row in df.iterrows():
        row_string = "\t".join(map(str, row))
        rows.append(row_string)
    return rows

# TODO Add the year summaries
def dataframe_to_text_tab(df: pd.DataFrame) -> [str]:
    
    # convert any enums to their values
    df = df_enum_columns_to_values(df)

    # Extract year and month
    df['year'] = [d.year for d in df['date']]
    df['month'] = [d.month for d in df['date']]

    # Reorder columns
    df = df[['package', 'year', 'month', 'ip_count', 'download_count']]

    formatted_output = dataframe_to_string_list(df)
    return formatted_output





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
