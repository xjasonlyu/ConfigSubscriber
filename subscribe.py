#!/usr/bin/env python3

import json
from os import path
from copy import deepcopy

# local modules
import parser
import policy
import toolkit as tk

# flask modules
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template


# Global Flask Instance
app = Flask(__name__)


def init_config():
    with open('config.json') as f:
        config = json.load(f)

    for _, c in config.items():
        c['filter'] = tk.convert2filter(c.get('filter'))

        for p in c.setdefault('policies', []):
            p.update(f=tk.convert2filter(p.get('f')))

    return config


# read config
CONFIG = init_config()


@app.route('/subscribe/<client>')
def subscribe(client):
    auth = request.args.get('auth')
    if auth not in CONFIG:
        return jsonify({'status': False, 'message': 'Auth challenge failed.'}), 401

    config = CONFIG[auth]

    client = client.lower()
    if client not in config['template']:
        return jsonify({'status': False, 'message': 'Client type not found.'}), 404

    try:
        items = tk.yaml_load(config['link'])
        raw_proxies = items['Proxy']
    except:
        return jsonify({'status': False, 'message': 'API call failed.'}), 500

    # get default parser if 'parser' field is empty
    group = policy.ProxyGroup(raw_proxies, parser.get(config.get('parser')))

    proxies = group.get_proxies(f=config['filter'])
    policies = (group.get_policy(**kwargs) for kwargs in config['policies'])

    return render_template(
        config['template'][client],
        proxies=proxies,
        policies=policies,
        **config.get('extras', {})
    )
