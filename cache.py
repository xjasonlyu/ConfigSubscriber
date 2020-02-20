#!/usr/bin/env python3

import os
from flask_caching import Cache


def init_cache(app, config):
    try:
        cache_config = config['settings']['cache']
    except KeyError:
        cache_config = {'CACHE_TYPE': 'null'}

    # Uppercase all keys
    cache_config = dict((k.upper(), v) for k, v in cache_config.items())

    cache = Cache(config=cache_config)
    cache.init_app(app)

    return cache
