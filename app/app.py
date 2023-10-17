from flask import Flask, make_response, Response, abort
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from markupsafe import escape
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # Set Matplotlib to use a non-GUI backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import math
import numpy

import app.app_helpers as ah
from db.db import DatabaseService, DatabaseConnectionInterface, TestDatabaseConnection
from db.db import DatabaseService, TestDatabaseConnection, PackageType


db_connection = TestDatabaseConnection()

import db.db as dbm
from db.db import PackageType, packge_type_exists

PATH = '/packages/stats'

# TODO: THIS IS MOCK DATABASE FOR INITIAL TESTING
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
# TODO Need to add format /bioc/bioc_2022_stats.tab
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



# Instantiate DatabaseService using TestDatabaseConnection
db = TestDatabaseConnection()
database_service = DatabaseService(db)

# Define the common data structure
common_data = {
    'bioconductor_link': 'bioc.html',
    'annotation_link': 'data-annotation.html',
    'experiment_link': 'data-experiment.html',
    'workflows_link': 'workflows.html',
    'generated_date': ah.app_config.today(),
    'data': [],  # populate this with real data from the database
}

# Define a dictionary to map package types to the top_count
top_counts = {
    'bioc': 75,
    'data-annotation': 30,
    'data-experiment': 15,
    'workflows': 5,
}

@app.route(PATH + '/<package_type>.html')
def show_packages_summary(package_type):
    # Check if the provided package_type is in the dictionary
    if package_type in top_counts:
        top_count = top_counts[package_type]
    else:
        abort(404)

    # Add category links for the top of the page
    category_links = {
        'bioc': ['data-experiment', 'data-annotation', 'workflows'],
        'data-annotation': ['bioc', 'data-experiment', 'workflows'],
        'data-experiment': ['bioc', 'data-annotation', 'workflows'],
        'workflows': ['bioc', 'data-experiment', 'data-annotation'],
    }

    category_links[package_type] = [link for link in category_links[package_type] if link != package_type]

    # Retrieve package data from the database using the database_service
    package_data = database_service.get_download_scores_for_category(PackageType(package_type))

    # Replace the static data with the data from the database
    common_data['data'] = [
        {'Packages': row['package'], 'Score': row['score']} for _, row in package_data.iterrows()
    ]

    return render_template('category.html', top_count=top_count, **common_data, category_links=category_links, package_type=package_type)

#fuction to plot the bar graphs
def make_barplot2ylog(title, barlabels,
                      barlabel_to_C1, C1_label, C1_color,
                      barlabel_to_C2, C2_label, C2_color, Cmax=None):
    c1_vals = []
    c2_vals = []
    Cmax0 = 0
    for label in barlabels:
        C1 = barlabel_to_C1[label]
        if C1 > Cmax0:
            Cmax0 = C1
        c1_vals.append(math.log10(1 + C1))
        C2 = barlabel_to_C2[label]
        if C2 > Cmax0:
            Cmax0 = C2
        c2_vals.append(math.log10(1 + C2))
    xticks = numpy.arange(len(c1_vals)) + 0.5
    width = 0.40  # the width of the bars

    fig, ax = plt.subplots(figsize=(9, 5))  # Create a figure and axis
    rects2 = ax.bar(xticks, c2_vals, width, align='edge', color=C2_color)
    rects1 = ax.bar(xticks, c1_vals, -width, align='edge', color=C1_color)
    xlabels = [label.replace('/', '\n') for label in barlabels]
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)

    if Cmax == None:
        Cmax = Cmax0
    if Cmax < 100:
        nb_pow10ticks = 3
    else:
        nb_pow10ticks = int(math.log10(Cmax)) + 2

    # Add labels, legend, and adjust plot settings as needed

    # Convert the plot to a PNG image
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)  # Close the figure to release resources

    # Encode the PNG image as base64
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    return image_base64

def write_HTML_stats_TABLE(months, month_to_C1, C1_label, C1_color, month_to_C2, C2_label, C2_color, allmonths_label, allmonths_c1, allmonths_c2=None):
    C1_style = 'style="text-align: right; background: %s"' % C1_color
    C2_style = 'style="text-align: right; background: %s"' % C2_color
    table_html = '<TABLE class="stats" align="center">\n'
    table_html += '<TR>'
    table_html += '<TH style="text-align: right">Month</TH>'
    table_html += '<TH %s>%s</TH>' % (C1_style, C1_label)
    table_html += '<TH %s>%s</TH>' % (C2_style, C2_label)
    table_html += '</TR>\n'

    sum2 = 0
    for month in months:
        c1 = month_to_C1[month]
        c2 = month_to_C2[month]
        sum2 += c2
        table_html += '<TR>'
        table_html += '<TD style="text-align: right">%s</TD>' % month
        table_html += '<TD %s>%d</TD>' % (C1_style, c1)
        table_html += '<TD %s>%d</TD>' % (C2_style, c2)
        table_html += '</TR>\n'

    if allmonths_c2 is None:
        allmonths_c2 = sum2
    elif allmonths_c2 != sum2:
        return "Error: allmonths_c2 != sum2"

    table_html += '<TR>'
    table_html += '<TH style="text-align: right">%s</TH>' % allmonths_label
    table_html += '<TH %s>%d</TH>' % (C1_style, allmonths_c1)
    table_html += '<TH %s>%d</TH>' % (C2_style, allmonths_c2)
    table_html += '</TR>\n'
    table_html += '</TABLE>\n'

    return table_html


#TODO implement for variable path 
#bioc/S4Vectors/
@app.route('/packages/stats/bioc/BiocVersion/')
def index7():
    months = ["Jan/2023", "Feb/2023", "Mar/2023", "Apr/2023", "May/2023", "Jun/2023", "Jul/2023", "Aug/2023", "Sep/2023", "Oct/2023", "Nov/2023", "Dec/2023"]
    month_to_C1 = {month: 1000 for month in months}
    month_to_C2 = {month: 2000 for month in months}
    allmonths_label = "2023"
    allmonths_c1 = sum(month_to_C1.values())
    allmonths_c2 = sum(month_to_C2.values())

    # Generate the barplot
    barplot_data = make_barplot2ylog("2023 Download Stats", months, month_to_C1, "C1 Label", "#aaaaff", month_to_C2, "C2 Label", "#ddddff")

    # Generate the HTML stats table
    stats_table = write_HTML_stats_TABLE(months, month_to_C1, "C1 Label", "#aaaaff", month_to_C2, "C2 Label", "2023", allmonths_c1, allmonths_c2)

    return render_template('stats-bioc.html', barplot_data=barplot_data, stats_table=stats_table)

if __name__ == '__main__':
    app.run(debug=True)


