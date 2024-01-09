"""_summary_.

Raises:
    NotImplementedError: _description_

Returns:
    _description_
"""
from collections import defaultdict
from datetime import date
import os

from flask import Blueprint, Response, abort, render_template, send_from_directory

import bioc_webstats.models as db
from bioc_webstats.models import PackageType, WebstatsInfo

# TODO @n1khilmane MOVE TO Config /Settings
URI_PATH_PREFIX = "/packages/stats"

# Map from incoming page name name to PackageType
category_map = {
    "bioc": {
        "category": PackageType.BIOC,
        "description": "software",
        "index_page": "index.html",
        "stem": "bioc",
        "tab_page_prefix": "bioc",
        "top": 75,
    },
    "data-annotation": {
        "category": PackageType.ANNOTATION,
        "description": "annotation",
        "index_page": "data-annotation.html",
        "stem": "data-annotation",
        "tab_page_prefix": "annotation",
        "top": 30,
    },
    "data-experiment": {
        "category": PackageType.EXPERIMENT,
        "description": "experiment",
        "index_page": "data-experiment.html",
        "stem": "data-experiment",
        "tab_page_prefix": "experiment",
        "top": 15,
    },
    "workflows": {
        "category": PackageType.WORKFLOWS,
        "description": "workflow",
        "index_page": "workflows.html",
        "stem": "workflows",
        "tab_page_prefix": "workflows",
        "top": 0,
    },
}

bp = Blueprint("stats", __name__, url_prefix=URI_PATH_PREFIX)


def split_to_dict_list(lst):
    """Transform int a dictionary based on first letter (case insensitive)."""
    result = defaultdict(list)

    for item in sorted(lst, key=lambda x: x[0].lower()):
        first_char = item[0][0].upper()  # Extract the first character of the string
        result[first_char].append(item)

    return result


def result_list_to_visual_list(rows):
    """Transform 3 column databas results to 4 column visual results with dense months."""
    dates = set([u[0] for u in rows])
    y0 = min(dates).year
    y1 = max(dates).year
    holes = (
        set([date(y, m + 1, 1) for y in range(y0, y1 + 1) for m in range(12)]) - dates
    )
    out = sorted(rows + [(w, 0, 0) for w in holes], key=lambda x: (-x[0].year, x[0]))
    return [
        {'year': dt.year, 'month': dt.strftime("%b") if dt.day == 1 else "all", 'unique_ips': ip, 'downloads': dl}
        for dt, ip, dl in out
    ]
 

def query_result_to_text(source):
    """Transform tabular query results to string.

    The strings are exact replicas of the .tab files found under
    www.bioconductor.org/packages/stats/.../<package>_stats.tab
    and <package>_scores.tab.

    The match exactly because they may be consumed by external software.

    Arguments:
        source -- A list of tuples in the form
            [(package, year, month, IP_count, Download_count)]
            or
            [(year, month, IP_count, Download_count)]

    Returns:
        A string in the format of a tab seperated file with one header row.

    """

    def process_one_package(package, rows):
        """For one package produce the result. If package is None, return 4 columns."""
        if package is None:
            k = ""
        else:
            k = package + "\t"

        out = result_list_to_visual_list(rows)
        return "\n".join(
             [f"{k}{u['year']}\t{u['month']}\t{u['unique_ips']}\t{u['downloads']}" for u in out])

    if source == []:
        return ""
    heading = "Year\tMonth\tNb_of_distinct_IPs\tNb_of_downloads"
    match len(source[0]):
        case 3:
            return heading + "\n" + (process_one_package(None, source))

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

@bp.route('/static/<path:filename>')
def static_files(filename):
    """Redirect requests to serve static files from root to the actual root of webstats."""
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_folder, filename)


@bp.route("/bioc/bioc_packages.txt")
def show_packages():
    """_summary_."""
    payload = db.Packages.get_package_names()
    text = ("\n").join(payload)
    return Response(text, content_type="text/plain")


@bp.route("<category>/<package>_pkg_scores.tab")
def show_package_scores(category, package):
    """_summary_."""
    # We match the legacy system, where both the path and the file_name included the category

    # if for category, in a form like this; /bio/bioc_pkg_scores.tab, or /data-annotation/annotation.pkg_scores.tab
    # `category_map` is a dictionary that maps the category names to their
    # corresponding information. Each category has a set of attributes such as the
    # package type, description, package index page, stem, tab page prefix, and
    # top count. This mapping is used in various parts of the code to retrieve the
    # relevant information based on the category name.
    selected_category = category_map.get(category, None)
    if selected_category is not None and package == selected_category["tab_page_prefix"]:
        payload = db.Stats.get_download_scores(category=selected_category["category"])
    else:
        abort(404)
    text = "Package\tDownload_score\n" + "\n".join([f"{x[0]}\t{x[1]}" for x in payload])
    return Response(text, content_type="text/plain")


@bp.route("<category>/<package>_stats.tab")
@bp.route("<category>/<package>_<year>_stats.tab")
@bp.route("<category>/<package_path>/<package>_stats.tab")
@bp.route("<category>/<package_path>/<package>_<year>_stats.tab")
def show_package_stats(category, package, package_path=None, year=None):
    """_summary_."""
    selected_category = category_map.get(category, None)
    if selected_category is None:
        abort(404)
    # If there is a second level in the path, then it can only be the package name
    # and that name must match the package name at the leaf
    # If the url is for all the packages in the repo,
    # it will be in the form /bio/bio_pkg_stats.tab and the year parameter will be 'pkg'
    if package_path is None and package == "bioc" or category == package:
        package = None
    elif package_path is not None and package_path != package:
        abort(404)
    # due to route spec, bioc_pkg_stats.tab and bioc_2023_stats.tab both end up here
    if package is None:
        if year == "pkg":
            payload = db.Stats.get_download_counts(selected_category["category"])
        else:
            payload = db.Categorystats.get_combined_counts(selected_category["category"], year)
    else:
        payload = db.Stats.get_download_counts(selected_category["category"], package, year)
        

    if payload == []:
        abort(404)

    return Response(query_result_to_text(payload), content_type="text/plain")


@bp.route("/")
@bp.route("/index.html")
@bp.route("/<category>.html")
def show_package_summary(category="bioc"):
    """Render package summary page."""
    selected_category = category_map.get(category, None)
    if selected_category is None:
        abort(404)
    category_enum = selected_category["category"]
    scores = db.Stats.get_download_scores(category_enum)
    url_list = [
        [u["index_page"], u["description"]]
        for u in category_map.values()
        if selected_category["category"] != u["category"]
    ]
    top_count = selected_category["top"]
    top = sorted(scores, key=lambda x: x[-1])[:top_count]

    return render_template(
        "category.html",
        top_count=top_count,
        category_links=url_list,
        category=category_enum,
        category_name=selected_category["description"],
        category_url_stem=selected_category["stem"],
        tab_page_prefix=selected_category["tab_page_prefix"],
        generated_date=WebstatsInfo.get_valid_thru_date(),
        top=top,
        scores=split_to_dict_list(scores),
    )


@bp.route("<category>/")
@bp.route("<category>/<package>")
@bp.route("<category>/<package>/")
@bp.route("<category>/index.html")
@bp.route("<category>/<package>/index.html")
def show_package_details(category, package=None):
    """Display package detials."""
    selected_category = category_map.get(category, None)
    if selected_category is None:
        abort(404)

    if package is None:
        source = db.Categorystats.get_combined_counts(selected_category["category"])
    else:
        source = db.Stats.get_download_counts(selected_category["category"], package)
    if len(source) == 0:
        abort(404)

    split = {}
    for t in source:
        split.setdefault(t[0].year, []).append(t)

    data_by_year = {year: result_list_to_visual_list(data) for year, data in split.items()}

    return render_template(
        "stats-bioc.html",
        category=category,
        category_name=selected_category["description"],
        category_stem=selected_category["stem"],
        category_index_page=('/').join((bp.url_prefix, selected_category["index_page"])),
        package=package,
        generated_date=WebstatsInfo.get_valid_thru_date(),
        data_by_year=data_by_year
    )
