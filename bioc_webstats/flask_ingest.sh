# TODO what is the correct directory for this script?
. .venv/bin/activate
export FLASK_APP="bioc_webstats.app:create_app('production', 'bioc/webstats/prod')"
flask ingest -c E1TVLJONPTUXV3
