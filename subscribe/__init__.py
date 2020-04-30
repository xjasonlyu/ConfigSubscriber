#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from importlib import import_module

from flask import Flask
from requests import Session

from .cache import init_cache
from .config import init_config

version_info = (0, 0, 2)
version = '.'.join(str(c) for c in version_info)

# global variables
app = cache = config = session = None


# Must be initiated before running
def init(conf_folder):
    global app, cache, config, session
    # Init Package Config
    config = init_config(conf_folder)

    # Init Flask App
    app = Flask(
        __name__,
        template_folder=config['templates_folder']
    )

    # Init Flask Caching
    cache = init_cache(app, config)

    # Init Requests Session
    session = Session()

    # Add Extensions
    app.jinja_env.add_extension('jinja2.ext.do')

    # Init App Route in views
    import_module('.views', package=__name__)
    # Init Template filters
    import_module('.filters', package=__name__)
    # Init Template globals
    import_module('.globals', package=__name__)
