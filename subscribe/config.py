#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from . import parser


class InitError(Exception):
    pass


def init_config(conf_folder) -> dict:
    # configuration directory
    conf_path = os.path.join(conf_folder, 'config.json')
    # load from json
    with open(conf_path) as f:
        config = json.load(f)

    # set default resources folder
    resources_folder = os.path.join(conf_folder, 'resources')
    config.setdefault('resources_folder', resources_folder)

    # set default templates folder
    templates_folder = os.path.join(conf_folder, 'templates')
    config.setdefault('templates_folder', templates_folder)

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
