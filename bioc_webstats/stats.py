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
from datetime import date

import matplotlib.pyplot as plt
import numpy

from flask import Blueprint, Response, abort, render_template

import bioc_webstats.models as db
from bioc_webstats.models import PackageType

# TODO Move to config
PATH = "/packages/stats"

bp = Blueprint("stats", __name__, url_prefix=PATH)

def split_to_dict_list(lst):
    """Transform int a dictionary based on first letter (case insensitive)."""

    result = defaultdict(list)

    for item in sorted(lst, key=lambda x: x[0].upper()):
        first_char = item[0][0].upper()  # Extract the first character of the string
        result[first_char].append(item)

    return result

def query_result_to_text(source):
    """Transforms tabular query results to string.
    
    The strings are exact replicas of the .tab files found under
    www.bioconductor.org/packages/stats/.../<package>_stats.tab 
    and <package>_scores.tab.
    
    The match exactly because they may be consumed by exteranl software.

    Arguments:
        source -- A list of tuples in the form
            [(package, year, month, IP_count, Download_count)]
            or
            [(year, month, IP_count, Download_count)]

    Returns:
        A string in the format of a tab seperated file with one header row.

    """

    def process_one_package(package, rows):
        """For one package produce the result. If package is None, return 4 columns"""

        if package is None:
            k = ""
        else:
            k = package + "\t"

        dates = set([u[0] for u in rows])
        y0 = min(dates).year
        y1 = max(dates).year
        holes = set([date(y, m + 1, 1) for y in range(y0, y1 + 1) for m in range(12)]) - dates
        out = sorted(rows + [(w, 0, 0) for w in holes], key=lambda x: x[0])

        return '\n'.join(
            [f"{k}{dt.year}\t{dt.strftime('%b') if dt.day == 1 else 'all'}\t{ip}\t{dl}"
                for dt, ip, dl in out])

    if source == []:
        return ""
    heading = "Year\tMonth\tNb_of_distinct_IPs\tNb_of_downloads"
    match len(source[0]):
        case 3:
            return heading + '\n' + (process_one_package(None, source))

        case 4:
            result = ["Package\t" + heading]
            split = {}
            for t in source:
                split.setdefault(t[0], []).append(t[1:])

            for k, v in split.items():
                result.append(process_one_package(k, v))

            return "\n".join(result)

        case _:
            raise AssertionError("query_result_to_text expects 4 or 5 columns")

@bp.route("/bioc/bioc_packages.txt", methods=["GET"])
def show_packages():
    """_summary_."""
    payload = db.Stats.get_package_names()
    text = ("\n").join(payload)
    return Response(text, content_type="text/plain")

@bp.route("<category>/<package>_pkg_scores.tab")
def show_package_scores(category, package):
    """_summary_."""
    # We match the legacy system, where both the path and the file_name included the category

    # if for category, in a form like this; /bio/bioc_pkg_scores.tab
    if category == package and db.package_type_exists(category):
        payload = db.Stats.get_download_scores(category=PackageType(category))
    else:
        abort(404)
    text = 'Package\tDownload_score\n' + '\n'.join([f"{x[0]}\t{x[1]}" for x in payload])
    return Response(text, content_type="text/plain")

# TODO Need to add format /bioc/bioc_2022_stats.tab
@bp.route("<category>/<package>_stats.tab")
@bp.route("<category>/<package>_<year>_stats.tab")
@bp.route("<category>/<package_path>/<package>_stats.tab")
@bp.route("<category>/<package_path>/<package>_<year>_stats.tab")
def show_package_stats(category, package, package_path=None, year=None):
    """_summary_."""
    if not db.package_type_exists(category):
        abort(404)
    # If there is a second level in the path, then it can only be the package name
    # and that name must match the package name at the leaf
    if package_path is not None and package_path != package:
        abort(404)
    # If the url is for all the packages in the repo,
    # it will be in the form /bio/bio_pkg_stats.tab and the year parameter will be 'pkg
    if category == package:
        # No package signals getting all the packages for the category
        package = None
        # due to route spec, bioc_pkg_stats.tab and bioc_2023_stats.tab both end up here
        if year == 'pkg':
            year = None
    payload = db.Stats.get_download_counts(PackageType(category), package, year)

    if payload == []:
        abort(404)

    return Response(query_result_to_text(payload), content_type="text/plain")

@bp.route("/")
@bp.route("/<category>.html")
def show_package_summary(category="index"):
    """_summary_."""
    
    # Map from incoming page name name to PackageType
    category_map = {
        "index": {"category": PackageType.BIOC, "description": "software", "stem": "index", "top": 75},
        "data-annotation": {"category": PackageType.ANNOTATION, "description": "annotation", "stem": "data-annotation", "top": 15},
        "data-experiment": {"category": PackageType.EXPERIMENT, "description": "experiment", "stem": "data-experiment", "top": 30},
        "workflows": {"category": PackageType.WORKFLOW, "description": "workflow", "stem": "workflows",  "top": 0}
    }

    # Get the package name if present
    selected_category = category_map.get(category, None)
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
        category=category_enum,
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

