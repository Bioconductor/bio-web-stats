#!/bin/bash
cd /var/www/bio-web-stats/
. .venv/bin/activate
gunicorn --bind 0.0.0.0:8000 --log-level debug -w 4 \
    --access-logfile /var/log/bioc-webstats/access.log \
    --error-logfile /var/log/bioc-webstats/error.log \
    'bioc_webstats.app:create_app()'
