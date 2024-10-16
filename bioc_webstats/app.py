"""
app.py

Create the flask application and inialize the environment

Summary: 
    This module implments the application factory, 
    as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

Description:
    All the run time parameters are read and various services are registered with the Flask infrastructure.

Notes:
    The run time parameters can come from the following sources. They are processed in the order
    shown here. A later source will overwrite an earlier source.
    1. Bootstrap parameters. Enviroment variables necessary to get started.
    2. configmodule.py. This defines the invariant default values for each parameter. Also defines manifest constants.
    3. An environmental parameter store. In specific, the AWS Systems Manager (SSM) Parameter Store.
    4. FLASK_* environment variables. For temporary overrides in production.
    5. ".env" files. Provides for parameters to be set based on their presence in this file.
    Useful for setting up test environments. Should never be used in production.

"""
import logging
import logging.handlers
import os
import sys

from flask import Flask, render_template
from werkzeug.utils import import_string

import bioc_webstats.aws_functions as aws
from bioc_webstats import commands, splash, stats
from bioc_webstats.configmodule import configuration_dictionary
from bioc_webstats.extensions import (
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    migrate,
)


def create_app(
    config_type=None,
    aws_parameter_path=None,
    enable_remote_debugging=False
):
    """The Application Factory. Set up the particular instance of the Flask class.

    Keyword Arguments:
        config_type -- The configmodule subclass object to use. Allowed values "production" and "development" (default: {"production"})
        aws_parameter_path -- If present, the the AWS System Manager Parameter Store will be searched for runtime parameters. See function aws.get_parameter_store_values for more information  (default: {None})
        enable_remote_debugging -- If True, the system wil attempt to enable the Visual Studio COde remote debugging protocl. See package ptvsd for details. (default: {False})

    Returns:
        A fully configured Flask App object.
    """    


    if enable_remote_debugging:
        # This will allow the use of the VS Code remote debugger.
        import ptvsd
        ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
        print("Waiting for debugger to attach...")
        ptvsd.wait_for_attach()

    app = Flask(__name__.split(".")[0])
    
    # Bootstrap variables
    if config_type is None:
        config_type = os.getenv('FLASK_ENV', config_type)
    app.config["ENV"] = config_type

    config_object_name = f"bioc_webstats.configmodule.{app.config["ENV"]}Config"

    # Populate the configuration from config and its sublcasses
    cfg = import_string(config_object_name)()
    app.config.from_object(cfg)

    # Next, load parameters from the SSM Parameter store.
    if aws_parameter_path is not None:
        param_dict = aws.get_parameter_store_values(app.config["AWS_PATH_PARAMETER"])
        xref = {}
        for u in configuration_dictionary:
            xref[u["Name"]] = u["FlaskName"]
        for k, v in param_dict.items():
            try:
                app.config[xref[k]] = v
            except Exception as e:
                logging.error(f"Could not map AWS SSM parameter {k}.")

    # Override with environment variables with FLASK_ prefix
    app.config.from_prefixed_env()

    # Exract database credentials from Secrets Manager
    if "DBCREDENTIALS" in app.config:
        app.config["DATABASE_URL"] = aws.aws_secret_to_psql_url(
            param_dict["db/credentials"], "us-east-1", "webstats"
        )



    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]
    # TODO SECRET_KEY from paraemter store
    app.config[
        "SECRET_KEY"
    ] = "1849cb85026145adc5164b9568d6afbde65351264f87c25aebdadc576ae662f5"

    configure_logger(app)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)

    # No debug toolbar for production
    if app.config["ENV"] != "production":
        debug_toolbar.init_app(app)

    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(stats.bp)
    # Exclude debuging tools if this is a production environment
    if app.config["ENV"] != "production":
        app.register_blueprint(splash.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    # Pass through http error codes if this is production
    if (app.config['ENV'] != 'production'):
        for errcode in [401, 404, 500]:
            app.errorhandler(errcode)(render_error)

    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.gendb)
    app.cli.add_command(commands.ingest)
    app.cli.add_command(commands.configp)
    app.cli.add_command(commands.packages)


def configure_logger(app):
    """Configure loggers."""

    logger = logging.getLogger("webstats")
    logger.setLevel(app.config["LOG_LEVEL"])
    log_file = app.config["LOG_FILEPATH"]

    # create the log file if necessasry    
    dir_path = os.path.dirname(log_file)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # Create the file if it does not exist
    with open(log_file, 'a'):
        os.utime(log_file, None)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=100000000, backupCount=5
    )
    file_handler.setLevel(app.config["LOG_LEVEL"])
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
