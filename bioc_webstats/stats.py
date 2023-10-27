"""_summary_.

Raises:
    NotImplementedError: _description_

Returns:
    _description_
"""
import base64
import math
from io import BytesIO
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy

# TODO: Kill pandas and numpy when done
import pandas as pd
from flask import Blueprint, Response, abort, render_template
from markupsafe import escape

import bioc_webstats.models as db
from bioc_webstats.models import PackageType

# TODO Move to config
PATH = "/packages/stats"

bp = Blueprint("stats", __name__, url_prefix=PATH)

# TODO - More work needed - the supervening code is in format_helpers.py and still needs work
def df_enum_columns_to_values(df: pd.DataFrame) -> pd.DataFrame:
    """_summary_."""
    for column in df.columns:
        # Check if any entry in the column is an instance of PackageType
        if any(isinstance(value, PackageType) for value in df[column]):
            df[column] = [e.value for e in df[column]]
    return df

# TODO These utility fuctions should be moved to a more appropriate location
def dataframe_to_string_list(df: pd.DataFrame) -> [str]:
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
    df["year"] = [d.year for d in df["date"]]
    df["month"] = [d.month for d in df["date"]]

    # Reorder columns
    df = df[["package", "year", "month", "ip_count", "download_count"]]

    formatted_output = dataframe_to_string_list(df)
    return formatted_output

def split_to_dict_list(lst):
    """Transform int a dictionary based on first letter (case insensitive)."""

    result = defaultdict(list)

    for item in sorted(lst, key=lambda x: x[0].upper()):
        first_char = item[0][0].upper()  # Extract the first character of the string
        result[first_char].append(item)

    return result

    """Split the list of tuples into a dictionary based on the letter of the package."""
    char_to_dict = {}
    result = {}

    for t in sorted(tuple_list, key=lambda x: x[0].upper()):

        first_char = t[0][0].upper()
        if first_char not in char_to_dict:
            char_to_dict[first_char] = {}
        char_to_dict[first_char][t[0]] = t[1:]

    for k, v in char_to_dict.items():
        result.append({k: v})

    return result

@bp.route("/bioc/bioc_packages.txt", methods=["GET"])
def show_packages():
    """_summary_."""
    payload = db.Stats.get_package_names()
    text = ("\n").join(payload)
    return Response(text, content_type="text/plain")


# TODO Need to add format /bioc/bioc_2022_stats.tab
@bp.route(
    "<package_type>/<package_type_in_filenames>_pkg_scores.tab"
    )
def show_pakages_scores(package_type, package_type_in_filenames):
    """_summary_."""
    # We match the legacy system, where both the path and the file_name included the category
    if package_type != package_type_in_filenames or not db.package_type_exists(package_type):
        abort(404)
    payload = db.Stats.get_download_scores(category=PackageType(package_type))
    text = "\n".join(
        [f"{x[0]}\t{x[1]}" for x in payload]
    )

    return Response(text, content_type="text/plain")

@bp.route("/")
@bp.route("/<package_type>.html")
def show_packages_summary(package_type="index"):
    """_summary_."""
    
    # Map from incoming page name name to PackageType
    category_map = {
        "index": {"category": PackageType.BIOC, "description": "software", "stem": "index", "top": 75},
        "data-annotation": {"category": PackageType.ANNOTATION, "description": "annotation", "stem": "data-annotation", "top": 15},
        "data-experiment": {"category": PackageType.EXPERIMENT, "description": "experiment", "stem": "data-experiment", "top": 30},
        "workflows": {"category": PackageType.WORKFLOW, "description": "workflow", "stem": "workflows",  "top": 0}
    }

    # Get the package name if present
    selected_category = category_map.get(package_type, None)
    if selected_category is None:
        abort(404)
    category_enum = selected_category["category"]
    scores = db.Stats.get_download_scores(category_enum)
    url_list = [[u["stem"], u["description"]] for u in category_map.values() if selected_category["category"] != u["category"]]
    top_count = selected_category["top"]
    top = sorted(scores, key=lambda x: x[-1])[:top_count]
    
    return render_template(
        "category.html",
        top_count=top_count,
        category_links=url_list,
        package_type=category_enum,
        category_name=selected_category["description"],
        category_url_stem=selected_category["stem"],
        generated_date=db.db_valid_thru_date(),
        top=top,
        scores=split_to_dict_list(scores),
    )


# fuction to plot the bar graphs
def make_barplot2ylog(
    title,
    barlabels,
    barlabel_to_c1,
    c1_label,
    c1_color,
    barlabel_to_c2,
    c2_label,
    c2_color,
    Cmax=None,
):
    """_summary_."""

    plt.use("Agg")  # Set Matplotlib to use a non-GUI backend

    c1_vals = []
    c2_vals = []
    Cmax0 = 0
    for label in barlabels:
        C1 = barlabel_to_c1[label]
        if C1 > Cmax0:
            Cmax0 = C1
        c1_vals.append(math.log10(1 + C1))
        C2 = barlabel_to_c2[label]
        if C2 > Cmax0:
            Cmax0 = C2
        c2_vals.append(math.log10(1 + C2))
    xticks = numpy.arange(len(c1_vals)) + 0.5
    width = 0.40  # the width of the bars

    fig, ax = plt.subplots(figsize=(9, 5))  # Create a figure and axis
    rects2 = ax.bar(xticks, c2_vals, width, align="edge", color=c2_color)
    rects1 = ax.bar(xticks, c1_vals, -width, align="edge", color=c1_color)
    xlabels = [label.replace("/", "\n") for label in barlabels]
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
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close(fig)  # Close the figure to release resources

    # Encode the PNG image as base64
    image_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return image_base64


def write_HTML_stats_TABLE(
    months,
    month_to_c1,
    c1_label,
    c1_color,
    month_to_c2,
    c2_label,
    c2_color,
    allmonths_label,
    allmonths_c1,
    allmonths_c2=None,
):
    c1_style = 'style="text-align: right; background: %s"' % c1_color
    c2_style = 'style="text-align: right; background: %s"' % c2_color
    table_html = '<TABLE class="stats" align="center">\n'
    table_html += "<TR>"
    table_html += '<TH style="text-align: right">Month</TH>'
    table_html += "<TH %s>%s</TH>" % (c1_style, c1_label)
    table_html += "<TH %s>%s</TH>" % (c2_style, c2_label)
    table_html += "</TR>\n"

    sum2 = 0
    for month in months:
        c1 = month_to_c1[month]
        c2 = month_to_c2[month]
        sum2 += c2
        table_html += "<TR>"
        table_html += '<TD style="text-align: right">%s</TD>' % month
        table_html += "<TD %s>%d</TD>" % (c1_style, c1)
        table_html += "<TD %s>%d</TD>" % (c2_style, c2)
        table_html += "</TR>\n"

    if allmonths_c2 is None:
        allmonths_c2 = sum2
    elif allmonths_c2 != sum2:
        return "Error: allmonths_c2 != sum2"

    table_html += "<TR>"
    table_html += '<TH style="text-align: right">%s</TH>' % allmonths_label
    table_html += "<TH %s>%d</TH>" % (c1_style, allmonths_c1)
    table_html += "<TH %s>%d</TH>" % (c2_style, allmonths_c2)
    table_html += "</TR>\n"
    table_html += "</TABLE>\n"

    return table_html

# @bp.route("<category>/")
# @bp.route("<category>/<package>.html")
def show_package_details(category, package="index"):
    """Display package detials."""
    # TODO Rewrite
    months = [
        "Jan/2023",
        "Feb/2023",
        "Mar/2023",
        "Apr/2023",
        "May/2023",
        "Jun/2023",
        "Jul/2023",
        "Aug/2023",
        "Sep/2023",
        "Oct/2023",
        "Nov/2023",
        "Dec/2023",
    ]
    month_to_c1 = {month: 1000 for month in months}
    month_to_c2 = {month: 2000 for month in months}
    allmonths_c1 = sum(month_to_c1.values())
    allmonths_c2 = sum(month_to_c2.values())

    # Generate the barplot
    barplot_data = make_barplot2ylog(
        "2023 Download Stats",
        months,
        month_to_c1,
        "C1 Label",
        "#aaaaff",
        month_to_c2,
        "C2 Label",
        "#ddddff",
    )

    # Generate the HTML stats table
    stats_table = write_HTML_stats_TABLE(
        months,
        month_to_c1,
        "C1 Label",
        "#aaaaff",
        month_to_c2,
        "C2 Label",
        "2023",
        allmonths_c1,
        allmonths_c2,
    )

    return render_template(
        "stats-bioc.html", barplot_data=barplot_data, stats_table=stats_table
    )


@bp.route('/<path:catch_all>')
def catch_all_route(catch_all):
    return f'You have reached the catch-all route: {catch_all}'

