# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
# import os
# from bioc_webstats.app import register_blueprints

# Check if the application is in production mode
# is_production = os.environ.get('FLASK_ENV') == 'production'

# TODO @n1khilmane here is were the prefix goes argument url_prefix 
# do we need this url_prefix ? since its a home page
blueprint = Blueprint("spash", __name__)


# if not is_production:
#     register_blueprints(blueprint)

# TODO @n1khilmane Exclude this from prod
@blueprint.route("/")
def home():
    """Home page for testing only."""
    targets = [
        "/",
        "/data-experiment.html",
        "/bioc/",
        "/bioc/bioc_packages.txt",
        "/bioc/bioc_2023_stats.tab",
        "/bioc/bioc_pkg_scores.tab",
        "/bioc/bioc_pkg_stats.tab",
        "/bioc/affy/",
        "/bioc/affy/affy_stats.tab",
        "/bioc/affy/affy_2023_stats.tab",
    ]

    return render_template("home.html", targets=targets)