#!/usr/bin/env python3

from os import path
from flask import request
from flask import render_template_string


def _read_template(name):
    t = path.join(path.dirname(__file__), name)
    with open(t) as f:
        return f.read()


def index():
    return render_template_string(
        _read_template('index.html'),
        title='༼ つ ◕_◕ ༽つ',
        message='(╯°□°)╯︵ ┻━┻',
    )


__plugins__ = {'/': index}
