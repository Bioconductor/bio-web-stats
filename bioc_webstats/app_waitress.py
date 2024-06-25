#!/usr/bin/env python3

from waitress import serve
from bioc_webstats import app
import logging
import sys

logging.basicConfig(stream=sys.stderr)

# TODO parameterize port 5000
if __name__ == "__main__":
    serve(app.create_app('Production', '/bioc/webstats/prod'), host='0.0.0.0', port=5000)