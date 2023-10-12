from flask import Flask, make_response, Response, abort
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import pandas as pd

import db.db as dbm
from dbquery import * # TODO REMOVE THIS

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
def get_packages():    
    payload = db.get_package_names()
    text = ('\n').join([row for row in payload['package']])
    return Response(text, content_type='text/plain')

# #bioc/bioc_pkg_scores.tab and package_stats.tab
@app.route(PATH + '/<package_type>/<package_type_in_filenames>_pkg_<scores_or_stats>.tab', methods=['GET'])
def get_pakages_scores(package_type, package_type_in_filenames, scores_or_stats):
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
    text = dataframe_to_string_list(payload)
    text = ('\n').join([row for row in text])
    return Response(text, content_type='text/plain')

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

    # Extract Year and Month
    df['Year'] = df['date'].dt.year
    df['Month'] = df['date'].dt.strftime('%b')

    # Drop the 'date' column
    df.drop('date', axis=1, inplace=True)

    # Ensure all months are covered for each package and year and fill missing values with 0
    all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    all_years = df['Year'].unique()
    all_packages = df['Package'].unique()
    idx = pd.MultiIndex.from_product([all_packages, all_years, all_months], names=['Package', 'Year', 'Month'])

    df.set_index(['Package', 'Year', 'Month'], inplace=True)
    df = df.reindex(idx).reset_index()
    df.fillna(0, inplace=True)

    # Reorder columns
    df = df[['Package', 'Year', 'Month', 'Nb_of_distinct_IPs', 'Nb_of_downloads']]

    # Process the second dataframe (data x year) call it df2
    # df2['Year'] = df2['date'].dt.year
    # df2['Month'] = 'YearSummary'  # Or any other desired label
    # df2.drop('date', axis=1, inplace=True)

    # # Concatenate and sort
    # final_df = pd.concat([df, df2], ignore_index=True)
    # final_df.sort_values(by=['Package', 'Year', 'Month'], inplace=True, key=lambda col: col.replace('YearSummary', 'Dec') if isinstance(col, str) else col)

    formatted_output = dataframe_to_string_list(df)
    return formatted_output



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
