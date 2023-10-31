#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/test4/bio-web-stats')  

from bioc_webstats.app import app as application