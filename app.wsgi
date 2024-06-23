#!/usr/bin/env python3
import logging
import sys

logging.basicConfig(stream=sys.stderr)

# TODO Delete? Given that this runs in a defined environment, we should already have the path
# Add the app's directory to the PYTHONPATH
sys.path.insert(0, '/var/www/bioc-webstats')

from bioc_webstats import app

application = app.create_app()