# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template

# TODO here is were the prefix goes argument url_prefix
blueprint = Blueprint("spash", __name__)
# TODO This is only for initial testing


# TODO Exclude this from prod
@blueprint.route("/")
def home():
    """Home page for testing only."""

    targets = ['/',
                '/bioc/',
                '/bioc/bioc_packages.txt',
                '/bioc/bioc_2022_stats.tab',
                '/bioc/bioc_pkg_scores.tab',
                '/bioc/bioc_pkg_stats.tab',
                '/bioc/affy/',
                '/bioc/affy/affy.tab',
                '/bioc/affy/affy_stats.tab'
            ]

    return render_template("home.html", targets=targets)
