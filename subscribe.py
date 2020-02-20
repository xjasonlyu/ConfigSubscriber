#!/usr/bin/env python3

import yaml
from datetime import datetime
from werkzeug.exceptions import HTTPException
from requests.exceptions import RequestException

# local modules
import policy
from toolkit import curl
from cache import init_cache
from config import init_config

# flask modules
from flask import abort
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template


# Global service config
config = init_config()

# Flask APP
app = Flask(__name__)

# Flask-Caching
cache = init_cache(app, config)


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
        message, code = f'CURL failed: {e}.', 500
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
    text = curl(cfg['link'], timeout=5, allow_redirects=True)
    # load from yaml text
    items = yaml.safe_load(text)
    if not items or not items.get('Proxy'):
        abort(500, 'Load proxies from YAML failed.')

    group = policy.ProxyGroup(items['Proxy'], sort=cfg['sort'], nodalize=cfg['parser'])

    proxies = group.get_proxies(f=cfg['filter'])
    policies = [group.get_policy(**kwargs) for kwargs in cfg['policies']]

    return render_template(
        config['templates'][client.upper()],
        url=request.url,
        date=datetime.now().strftime('%Y%m%d'),
        proxies=proxies,
        policies=policies,
        extras=cfg['extras']
    )


if __name__ == '__main__':
    app.run()
