#!/usr/bin/env python3

import json
from flask import request
from flask import Response


def get_ip():
    if request.path == '/ip':
        return Response(request.remote_addr, mimetype='text/plain')
    elif request.path == '/jsonip':
        mime = 'application/json'
        result = json.dumps({ 'ip': request.remote_addr })
    # callback
    f = request.args.get('callback')
    if f:
        mime = 'text/javascript'
        result = f'{f}({result});'
    return Response(result, mimetype=mime)
