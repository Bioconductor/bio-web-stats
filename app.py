from waitress import serve
from bioc_webstats import app

# TODO parameterize port 5000
if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)