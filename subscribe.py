#!/usr/bin/env python3

import re
import json
import yaml
import requests
from os import path

# local modules
import parser
import policy

# flask modules
from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import render_template_string


# Global Flask Instance
app = Flask(__name__)

# auth & config dict
__CONFIG__ = None


def init():
    global __CONFIG__

    with open(path.join(path.dirname(__file__), 'config.json')) as f:
        __CONFIG__ = json.load(f)

    for _, data in __CONFIG__.items():
        if data.get('filter'):
            # TODO: replace eval with safer operation
            data['filter'] = eval(data['filter'])

        for opt in data['groups']:
            if opt.get('f'):
                # TODO: same with above
                opt['f'] = eval(opt['f'])


init()


# simple curl in python version
def curl(url: str, timeout: int = None, allow_redirects: bool = False) -> str:
    # process URL
    if not re.match('(http|https|file)://', url):
        url = 'http://' + url
    # file protocol
    if url.startswith('file://'):
        url = url[7:]
        if not path.exists(url):
            return ''
        with open(url, 'r') as f:
            return f.read()
    # curl headers
    headers = {
        'User-Agent': 'curl',
        'Accept': '*/*'
    }
    # requests session
    s = requests.Session()
    s.trust_env = False
    # requests
    try:
        r = s.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
        r.raise_for_status()
        return r.text
    except:
        return ''


def get_proxies(url):
    text = curl(url, 5, True)
    items = yaml.safe_load(text)
    return items['Proxy']


def get_template(name):
    template_file = path.join(path.dirname(__file__), 'templates', name)
    return curl('file://'+path.abspath(template_file))


@app.route('/subscribe/<client>')
def subscribe(client):
    client = client.lower()
    if client not in config['template']:
        return jsonify({'status': False, 'message': 'Client type not found.'}), 404

    auth = request.args.get('auth')
    if auth not in __CONFIG__:
        return jsonify({'status': False, 'message': 'Auth challenge failed.'}), 401

    config = __CONFIG__[auth]

    try:
        raw_proxies = get_proxies(config['link'])
    except:
        return jsonify({'status': False, 'message': 'Fetch link failed.'}), 500

    # get default parser if 'parser' field is empty
    group = policy.ProxyGroup(raw_proxies, parser.get(config.get('parser')))

    if config.get('filter'):
        proxies = group.get_proxies(f=config['filter'])
    else:
        proxies = group.get_proxies()

    policies = (group.get_policies(**kwargs) for kwargs in config['groups'])

    return render_template_string(
        source=get_template(config['template'][client]),
        proxies=proxies,
        policies=policies,
        **config.get('extras', {})
    )
