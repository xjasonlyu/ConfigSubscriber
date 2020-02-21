#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package variables
from . import app
from . import cache
from . import config

# local modules
from . import policy
from .toolkit import fetch_url

# flask modules
from flask import abort
from flask import jsonify
from flask import request
from flask import render_template

import yaml
from werkzeug.exceptions import HTTPException
from requests.exceptions import RequestException


@app.errorhandler(Exception)
def return_json_if_error_occurred(e):
    if isinstance(e, HTTPException):
        if len(e.description) < 40:
            message, code = e.description, e.code
        else:
            message, code = f'{e.code} {e.name}.', e.code
    elif isinstance(e, yaml.YAMLError):
        message, code = f'Parse YAML file error.', 500
    elif isinstance(e, (FileNotFoundError, RequestException)):
        message, code = f'Fetch URL failed: {e}.', 500
    else:
        message, code = f'API call failed: {e}.', 500
    # JSON responses
    return jsonify(status=False, message=message), code


@app.route('/subscribe/<client>', methods=['GET'])
@cache.cached(query_string=True)
def subscribe(client):
    # authorization check
    auth = request.args.get('auth')
    if auth not in config['subscriptions'].keys():
        abort(401, 'Auth challenge failed.')

    if client.upper() not in config['templates']:
        abort(404, 'Client template not found.')

    # subscription detail config
    cfg = config['subscriptions'][auth]

    # fetch original subscription file
    text = fetch_url(cfg['link'])
    # load from yaml text
    items = yaml.safe_load(text)
    if not items or not items.get('Proxy'):
        abort(500, 'Load proxies from YAML failed.')

    group = policy.ProxyGroup(items['Proxy'], f=cfg['filter'], sort=cfg['sort'], nodalize=cfg['parser'])

    policies = [group.get_policy(**kwargs) for kwargs in cfg['policies']]

    return render_template(
        config['templates'][client.upper()],
        proxies=group.proxies,
        policies=policies,
        extras=cfg['extras']
    )
