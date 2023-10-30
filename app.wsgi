#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)

# Add the directory containing your Flask app to the Python path
sys.path.insert(0, '/path/to/your/app')

# Import your Flask app
from your_app_module import app as application

# This ensures that your application runs when the script is loaded by mod_wsgi.
if __name__ == '__main__':
    application.run()
