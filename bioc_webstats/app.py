# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import sys
import os
from flask import Flask, render_template
from werkzeug.utils import import_string
from bioc_webstats import commands, splash, stats
import bioc_webstats.aws_functions as aws

from bioc_webstats.extensions import (
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    migrate,
)

def create_app(config_type="Production"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object_name: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    
    config_object_name = f"bioc_webstats.configmodule.{config_type}Config"

    # Populate the configuration from config and its sublcasses
    cfg = import_string(config_object_name)()
    app.config.from_object(cfg)
    # Override with environment variables with FLASK_ prefix
    app.config.from_prefixed_env()

    if 'AWS_PARAMETER_PATH' not in app.config:
        param_dict = {}
    else:
        # TODO try/except/raise for ToekenRetrievalError
        param_dict = aws.get_parameter_store_values(app.config['AWS_PARAMETER_PATH'])
    if 'db/credentials' in param_dict:
        app.config["DATABASE_URL"] = aws.aws_secret_to_psql_url(param_dict['db/credentials'], "us-east-1", "webstats")

    # TODO Issue: how to override db/credentials with DATABASE_URL. Answer use "special arn-to-url scheme"
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["DATABASE_URL"]
    # TODO SECRET_KEY from paraemter store
    app.config["SECRET_KEY"]="1849cb85026145adc5164b9568d6afbde65351264f87c25aebdadc576ae662f5"

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)
    return app


def register_extensions(app):
    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    return None

def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(stats.bp)
    # Exclude debuging tools if this is a production environment
    if app.config['ENV'] != 'production':
        app.register_blueprint(splash.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

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

def configure_logger(app):
    """Configure loggers."""
    # TODO PARAMETERIZE
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)
