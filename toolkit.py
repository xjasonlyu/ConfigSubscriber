#!/usr/bin/env python3

import re
import json
import yaml
import requests
from os import path


# access dict with dot
class Dotty:

    def __init__(self, data):
        self._data = dict(data)

    def __getattr__(self, item):
        return self._data.get(item)


# export dotty function
def dotty(data=None):
    if data is None:
        data = {}
    return Dotty(data)


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
    r = s.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
    r.raise_for_status()
    return r.text


# simple function to load json
def json_load(url):
    if not re.match('(http|https)://', url):
        url = 'file://' + path.abspath(url)
    text = curl(url)
    return json.loads(text)


# simple function to load yaml
def yaml_load(url):
    if not re.match('(http|https)://', url):
        url = 'file://' + path.abspath(url)
    text = curl(url)
    return yaml.safe_load(text)


# convert raw string to filter function
def convert2filter(raw):
    if not raw:
        return lambda _: True
    return eval(raw)
