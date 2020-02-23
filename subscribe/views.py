#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package variables
from . import app
from . import cache
from . import config

# Flask modules
from flask import abort
from flask import jsonify
from flask import request
from flask import Response
from flask import render_template

# Exceptions
from jinja2.exceptions import TemplateError
from werkzeug.exceptions import HTTPException


@app.errorhandler(Exception)
def return_json_if_error_occurred(e):
    if isinstance(e, HTTPException):
        if len(e.description) < 40:
            message, code = e.description, e.code
        else:
            message, code = f'{e.code} {e.name}.', e.code
    elif isinstance(e, TemplateError):
        message, code = f'Template error: {e}.', 500
    else:
        message, code = f'Internal error: {e}.', 500
    # JSON responses
    return jsonify(status=False, message=message), code


@app.route('/subscribe/<client>', methods=['GET'])
@cache.cached(query_string=True)
def subscribe(client):
    # authorization check
    auth = request.args.get('auth')
    if auth not in config['subscriptions'].keys():
        abort(401, 'Auth challenge failed.')

    return Response(
        render_template(
            'index.j2',
            client=client,
            cfg=config['subscriptions'][auth]
        ),
        mimetype='text/plain'
    )
