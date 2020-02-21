#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

from . import parser
from .toolkit import str2sort
from .toolkit import str2filter


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

    # set default templates value
    templates = config.setdefault('templates', {})
    # lowercase all keys
    config['templates'] = dict((k.upper(), v) for k, v in templates.items())
    # set default subscriptions value
    config.setdefault('subscriptions', {})

    # process config
    for auth, body in config['subscriptions'].items():
        if len(auth) < 8:
            raise InitError('Auth length should be at least > 8!')

        if not body.get('link'):
            raise InitError('Subscribe link url is required!')

        # convert string to function
        body['sort'] = str2sort(body.get('sort'))
        body['filter'] = str2filter(body.get('filter'))
        body['parser'] = parser.get(body.get('parser'))

        # set default values
        body.setdefault('extras', {})
        body.setdefault('policies', [])

        # set default policies field
        for policy in body['policies']:
            # set default policy filter if empty
            policy.update(f=str2filter(policy.get('f')))

    return config
