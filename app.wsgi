#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/test4/bio-web-stats')

from bioc_webstats import app
application = app.create_app()

#!/usr/bin/python3
import sys
import logging
import site
from os import environ
from os.path import join, dirname, realpath

logging.basicConfig(stream=sys.stderr)

# Add the site-packages of the chosen virtualenv to work with
virtualenv_dir = '.venv'
virtualenv_site_packages = join(virtualenv_dir, 'lib/python3.X/site-packages')
site.addsitedir(virtualenv_site_packages)

# Add the app's directory to the PYTHONPATH
sys.path.insert(0, '/var/www/bio-web-stats')

# Activate the virtual environment
activate_this = join(virtualenv_dir, 'bin/activate_this.py')
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

from bioc_webstats import app

