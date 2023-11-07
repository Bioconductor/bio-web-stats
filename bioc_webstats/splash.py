# -*- coding: utf-8 -*-
"""User views."""
from flask import Blueprint, render_template
import os

is_production = os.environ.get('FLASK_ENV') == 'production'

if not is_production:
    blueprint = Blueprint("spash", __name__)


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