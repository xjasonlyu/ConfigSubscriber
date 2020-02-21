#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
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

# Init App Route in views
import_module('subscribe.views')
# Init Template filters
import_module('subscribe.filters')
