#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask_caching import Cache


def init_cache(app, config):
    cache_config = None

    if not app.debug:
        cache_config = config['settings'].get('cache')

    if cache_config is None:
        cache_config = {
            'CACHE_TYPE': 'null',
            'CACHE_NO_NULL_WARNING': True
            }

    # Uppercase all keys
    cache_config = dict((k.upper(), v) for k, v in cache_config.items())

    cache = Cache(config=cache_config)
    cache.init_app(app)

    return cache
