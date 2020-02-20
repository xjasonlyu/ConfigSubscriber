#!/usr/bin/env python3

import yaml
from datetime import datetime
from requests.exceptions import RequestException

# local modules
import policy
from exceptions import *
from toolkit import curl
from cache import init_cache
from config import init_config

# flask modules
from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template


# Global service config
config = init_config()

# Flask APP
app = Flask(__name__)

# Flask-Caching
cache = init_cache(config)
cache.init_app(app)


def return_json_if_error_occurred(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Unauthorized:
            msg, code = 'Auth challenge failed.', 401
        except ClientNotFound:
            msg, code = 'Client type not found.', 404
        except RequestException as e:
            msg, code = f'Request failed: {e}.', 500
        except Exception as e:
            msg, code = f'API call failed: {e}.', 500
        # json responses
        return jsonify({'status': False, 'message': msg}), code
    return wrapper


@app.route('/subscribe/<client>', methods=['GET'])
@return_json_if_error_occurred
@cache.cached(query_string=True)
def subscribe(client):
    # authorization check
    auth = request.args.get('auth')
    if auth not in config['subscriptions'].keys():
        raise Unauthorized()

    if client.upper() not in config['templates']:
        raise ClientNotFound()

    # subscription detail config
    cfg = config['subscriptions'][auth]

    # fetch original subscription file
    text = curl(cfg['link'], timeout=5, allow_redirects=True)
    # load from yaml text
    items = yaml.safe_load(text)
    raw_proxies = items['Proxy']

    group = policy.ProxyGroup(raw_proxies, sort=cfg['sort'], nodalize=cfg['parser'])

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
