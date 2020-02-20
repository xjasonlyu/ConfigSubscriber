#!/usr/bin/env python3

import os
import json
import yaml
from requests.exceptions import RequestException

# local modules
import parser
import policy
from toolkit import *
from exceptions import *

# flask modules
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template


# Global Flask Instance
app = Flask(__name__)

def _init_config() -> dict:
    with open(os.environ.get('CONFIG', 'config.json')) as f:
        config = json.load(f)

    for _, c in config.items():
        # set default func if empty
        c['sort'] = str2sort(c.get('sort'))
        c['filter'] = str2filter(c.get('filter'))

        # set default policies field
        for p in c.setdefault('policies', []):
            # set default policy filter if empty
            p.update(f=str2filter(p.get('f')))

    return config


# read config
CONFIG = _init_config()


def return_json_if_error_occurred(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Unauthorized:
            return jsonify({'status': False, 'message': 'Auth challenge failed.'}), 401
        except ClientNotFound:
            return jsonify({'status': False, 'message': 'Client type not found.'}), 404
        except RequestException as e:
            return jsonify({'status': False, 'message': f'Request failed: {e}.'}), 500
        except Exception as e:
            return jsonify({'status': False, 'message': f'API call failed: {e}.'}), 500
    return wrapper


@app.route('/subscribe/<client>', methods=['GET'])
@return_json_if_error_occurred
def subscribe(client):
    auth = request.args.get('auth')
    if auth not in CONFIG.keys():
        raise Unauthorized()

    # auth -> config
    cfg = CONFIG[auth]

    client = client.lower()
    if client not in cfg['template']:
        raise ClientNotFound()

    text = curl(cfg['link'], timeout=5, allow_redirects=True)
    items = yaml.safe_load(text)
    raw_proxies = items['Proxy']

    # get default parser if 'parser' field is empty
    group = policy.ProxyGroup(raw_proxies, sort=cfg.get('sort'), 
                                nodalize=parser.get(cfg.get('parser')))

    proxies = group.get_proxies(f=cfg['filter'])
    policies = [group.get_policy(**kwargs) for kwargs in cfg['policies']]

    return render_template(
        cfg['template'][client],
        url=request.url,
        date=date(),
        proxies=proxies,
        policies=policies,
        extras=cfg.get('extras', {})
    )


if __name__ == '__main__':
    app.run()
