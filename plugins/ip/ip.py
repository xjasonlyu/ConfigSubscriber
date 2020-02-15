#!/usr/bin/env python3

import json
from flask import request
from flask import Response


def get_ip():
    result = request.remote_addr
    mime = 'text/plain'
    if request.path == '/ip':
        return Response(result, mimetype=mime)
    elif request.path == '/jsonip':
        mime = 'application/json'
        result = json.dumps({'ip': result})
    # callback
    f = request.args.get('callback')
    if f:
        mime = 'text/javascript'
        result = f'{f}({result});'
    return Response(result, mimetype=mime)
