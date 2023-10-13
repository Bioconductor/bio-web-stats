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

@app.route('/packages/stats/', defaults={'package_type': 'default'})
@app.route(PATH + '/<package_type>.html')
def show_packages_(package_type):
    if package_type is 'default':
        # This is the default route, so load the data and template accordingly
        df = pd.DataFrame({
            'Packages': ['S4Vectors', 'Biobase', 'BiocParallel', 'Package4', 'Package5', 'Package6'],
            'Score': [90, 85, 88, 95, 75, 80]
        })
        records = df.to_dict(orient='records')
        template_name = 'index.html'
    
    elif package_type == 'bioc':
        # If 'package_type' is 'bioc', load a different template and data
        df = pd.DataFrame({
            'Packages': ['S4Vectors', 'Biobase', 'BiocParallel', 'Package4', 'Package5', 'Package6'],
            'Score': [90, 85, 88, 95, 75, 80]
        })
        records = df.to_dict(orient='records')
        template_name = 'bioc.html'
        
    elif package_type == 'data-annotation':
        template_name = 'data-annotation.html'
        
        df = pd.DataFrame({
        'Packages': ['GenomeInfoDbData', 'GO.db', 'org.Hs.eg.db', 'Package4', 'Package5', 'Package6'],
        'Score': [90, 85, 88, 95, 75, 80]
        })
        records = df.to_dict(orient='records')

    elif package_type == 'data-experiment':
        template_name = 'data-experiment.html'
        
        df = pd.DataFrame({
        'Packages': ['ALL', 'TCGAbiolinksGUI.data', 'celldex', 'Package4', 'Package5', 'Package6'],
        'Score': [90, 85, 88, 95, 75, 80]
        })
        records = df.to_dict(orient='records')
    
    elif package_type == 'workflows':
        template_name = 'workflows.html'
        
        df = pd.DataFrame({
        'Packages': ['GenomeInfoDbData', 'GO.db', 'org.Hs.eg.db', 'Package4', 'Package5', 'Package6'],
        'Score': [90, 85, 88, 95, 75, 80]
        })
        records = df.to_dict(orient='records')

    else:
        # Handle the case where package_type is not recognized
        return "Package type not found"

    return render_template(template_name, records=records)



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


@app.route('/packages/stats/bioc/BiocVersion/')
def index5():
    # Dummy data - Replace with your data retrieval logic
    barlabels = ["Jan/2023", "Feb/2023", "Mar/2023", "Apr/2023", "May/2023", "Jun/2023", "Jul/2023", "Aug/2023", "Sep/2023", "Oct/2023", "Nov/2023", "Dec/2023"]
    barlabel_to_C1 = {"Jan/2023": 3165198, "Feb/2023": 3488622, "Mar/2023": 4407007, "Apr/2023": 3892123, "May/2023": 4029362, "Jun/2023": 3623651, "Jul/2023": 3531188, "Aug/2023": 3718150, "Sep/2023": 3509979, "Oct/2023": 835681, "Nov/2023": 0, "Dec/2023": 0}
    barlabel_to_C2 = {"Jan/2023": 96471, "Feb/2023": 108380, "Mar/2023": 134470, "Apr/2023": 126179, "May/2023": 127681, "Jun/2023": 122621, "Jul/2023": 122530, "Aug/2023": 121541, "Sep/2023": 130785, "Oct/2023": 43192, "Nov/2023": 0, "Dec/2023": 0}

    title = "Download Stats for Bioconductor Software Repository (2023)"
    
    image_base64 = make_barplot2ylog(title, barlabels, barlabel_to_C1, 'C1 Label', 'blue', barlabel_to_C2, 'C2 Label', 'red')

    return render_template('stats-bioc.html', image_base64=image_base64)













if __name__ == '__main__':
    app.run(debug=True)










# #bioc/S4Vectors/
# @app.route('/packages/stats/<package_type>/<package_name>/', methods=['GET'])
# def get_exixsting_package(package_type, package_name):
#     



# #ROOT
# @app.route('/packages/stats/', methods=['GET'])


# #BIOC
# @app.route('/packages/stats/bioc', methods=['GET'])
