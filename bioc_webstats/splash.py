# -*- coding: utf-8 -*-
"""User views."""
import os

<<<<<<< Updated upstream
from flask import Blueprint, render_template

=======
# TODO this should be global variable ENV, not external environment FLASK_ENV
>>>>>>> Stashed changes
is_production = os.environ.get('FLASK_ENV') == 'production'

if not is_production:
    blueprint = Blueprint("spash", __name__)


    @blueprint.route("/")
    def home():
        """Home page for testing only."""
        targets = [
            "/bioc/",
            "/bioc/affy/",
            "/bioc/affy/affy_2023_stats.tab",
            "/bioc/affy/affy_stats.tab",
            "/bioc/bioc_2023_stats.tab",
            "/bioc/bioc_packages.txt",
            "/bioc/bioc_pkg_scores.tab",
            "/bioc/bioc_pkg_stats.tab",
            "/bioc/bioc_stats.tab",
            "/bioc/bioc_stats.tab",
            "/data-experiment.html",
            "/data-experiment/ABAData/",
            "/data-experiment/ABAData/ABAData_2024_stats.tab",
            "/data-experiment/ABAData/ABAData_stats.tab",
            "/data-experiment/experiment_2023_stats.tab",
            "/data-experiment/experiment_2023_stats.tab",
            "/data-experiment/experiment_pkg_scores.tab",
            "/data-experiment/experiment_pkg_stats.tab",
            "/data-experiment/experiment_stats.tab",
                "/data-experiment/ABAData/",
            "/data-experiment/ABAData/ABAData_2023_stats.tab",
            "/data-experiment/ABAData/ABAData_stats.tab",
            ]

        return render_template("home.html", targets=targets)