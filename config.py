#!/usr/bin/env python3

import os
import json

import parser
from toolkit import str2sort
from toolkit import str2filter
from exceptions import InitError


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

    # set default values
    config.setdefault('subscribe', {})
    config.setdefault('templates', {})

    # process config
    for auth, body in config['subscribe'].items():
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
