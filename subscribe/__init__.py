#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from requests import Session
from importlib import import_module

# Package Import
from .cache import init_cache
from .config import init_config

# Init Flask App
app = Flask(__name__)

# Init Package Config
config = init_config()

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
