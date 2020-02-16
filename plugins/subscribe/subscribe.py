#!/usr/bin/env python3

import yaml
from os import path

from . import policy
from . import services

# User instances
from . import instances

from flask import jsonify
from flask import request
from flask import Response
from flask import render_template_string


# auth code mapping
AUTH_MAP = dict()


def init():
    for m in instances.__EXPORT__:
        m.SERVICE = m.SERVICE.upper()
        AUTH_MAP[m.AUTH] = m


init()


def get_proxies(url):
    content = services.utils.curl(url, 5, True)
    items = yaml.safe_load(content.decode())
    return items['Proxy']


def get_template(name):
    template_file = path.join(path.dirname(__file__), 'templates', name)
    with open(template_file) as f:
        return f.read()


def subscribe(client):
    client = policy.__CLIENTS__.get(client.lower())
    if client is None:
        return jsonify({'status': False, 'message': 'Client type not found.'}), 404

    auth = request.args.get('auth')
    if not auth or auth not in AUTH_MAP:
        return jsonify({'status': False, 'message': 'Auth challenge failed.'}), 401

    m = AUTH_MAP[auth]

    if hasattr(m, 'PROXIES_FILTER'):
        group = policy.Group(get_proxies(m.LINK), services.__NODE__[m.SERVICE], m.PROXIES_FILTER)
    else:
        group = policy.Group(get_proxies(m.LINK), services.__NODE__[m.SERVICE])

    proxies = group.get_proxies(client)
    policies = '\n'.join([group.get_policy(**kwarg, client=client) for kwarg in m.POLICIES_ARGS])

    return render_template_string(
        source=get_template(m.TEMPLATE[client]),
        proxies=proxies,
        names=m.NAMES,
        policies=policies,
    )
