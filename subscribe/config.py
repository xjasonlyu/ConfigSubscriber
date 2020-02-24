#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from . import parser


class InitError(Exception):
    pass


def init_config() -> dict:
    if os.environ.get('CONFIG'):
        # get config path from ENV
        conf_path = os.environ['CONFIG']
    else:
        # default config path
        conf_path = 'config.json'

    # load from json
    with open(conf_path) as f:
        config = json.load(f)

    # set default resource dir
    config.setdefault('resource_dir', '.')

    # set default value
    config.setdefault('settings', {})
    config.setdefault('subscriptions', {})

    # process config
    for auth, body in config['subscriptions'].items():
        if len(auth) < 8:
            raise InitError('Auth length should be at least > 8!')

        if not body.get('link'):
            raise InitError('Subscribe link url is required!')

        if not body.get('template'):
            raise InitError('Subscribe template is required!')

        # convert string to function
        body['parser'] = parser.get(body.get('parser'))

        # set default values
        body.setdefault('sort', None)
        body.setdefault('filter', None)
        body.setdefault('interval', 0)
        body.setdefault('extras', {})

    return config
