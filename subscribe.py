#!/usr/bin/env python3

import json
import yaml

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


def init_config() -> dict:
    with open('config.json') as f:
        config = json.load(f)

    for _, c in config.items():
        # set default proxies filter if empty
        c['filter'] = tk.str2filter(c.get('filter'))

        # set default policies field
        for p in c.setdefault('policies', []):
            # set default policy filter if empty
            p.update(f=tk.str2filter(p.get('f')))

    return config


# read config
CONFIG = init_config()


@app.route('/subscribe/<client>')
def subscribe(client):
    auth = request.args.get('auth')
    if auth not in CONFIG.keys():
        return jsonify({'status': False, 'message': 'Auth challenge failed.'}), 401

    # auth -> config
    cfg = CONFIG[auth]

    client = client.lower()
    if client not in cfg['template']:
        return jsonify({'status': False, 'message': 'Client type not found.'}), 404

    try:
        text = tk.curl(cfg['link'], timeout=5)
        items = yaml.safe_load(text)
        raw_proxies = items['Proxy']
    except:
        return jsonify({'status': False, 'message': 'Fetch original config failed.'}), 500

    try:
        # get default parser if 'parser' field is empty
        group = policy.ProxyGroup(raw_proxies, parser.get(cfg.get('parser')))
    except parser.ParseError as e:
        return jsonify({'status': False, 'message': f'Parse config failed: {e}'}), 500

    proxies = group.get_proxies(f=cfg['filter'])
    policies = (group.get_policy(**kwargs) for kwargs in cfg['policies'])

    return render_template(
        cfg['template'][client],
        proxies=proxies,
        policies=policies,
        **cfg.get('extras', {})
    )
