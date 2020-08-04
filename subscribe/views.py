#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Response
from flask import abort
from flask import jsonify
from flask import render_template
from flask import request
from jinja2.exceptions import TemplateError
from werkzeug.exceptions import HTTPException

from . import app
from . import cache
from . import config
from . import ruleset


@app.errorhandler(Exception)
def return_json_if_error_occurred(e):
    if app.debug:
        # log errors
        app.log_exception(e)

    if isinstance(e, HTTPException):
        if len(e.description) < 40:
            description = e.description
        else:
            description = f'{e.code} {e.name}.'
        message, code = description, e.code
    elif isinstance(e, TemplateError):
        message, code = f'Template Error.', 500
    elif isinstance(e, IOError):
        message, code = f'Internal IO Error.', 500
    else:
        message, code = f'Unknown Internal Error.', 500
    # JSON responses
    return jsonify(status=False, message=message), code


@app.route('/ruleset/<path:rule>', methods=['GET'])
@cache.cached(query_string=True)
def api_ruleset(rule):
    # priority: local > remote
    try:
        # try serve local
        content = ruleset.serve_local(rule)
    except TemplateError:
        # if failed then try serve remote
        content = ruleset.serve_remote(rule)

    if not content:
        abort(404, 'Ruleset not found.')
    else:
        return Response(content, mimetype='text/plain')


@app.route('/subscribe/<client>', methods=['GET'])
@cache.cached(query_string=True)
def api_subscribe(client):
    # authorization check
    auth = request.args.get('auth')
    if auth not in config['subscriptions'].keys():
        abort(401, 'Auth challenge failed.')

    return Response(
        render_template(
            'index.j2',
            client=client,
            args=request.args,
            cfg=config['subscriptions'][auth]
        ),
        mimetype='text/plain'
    )
