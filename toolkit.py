#!/usr/bin/env python3

import re
import requests
from os import path


# access dict with dot
class Dotty(dict):

    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise AttributeError('Dictionary must be type of dict')
        else:
            self._data = data
        super(Dotty, self).__init__(data)

    def __getattr__(self, key):
        if key in self.__dict__:
            return getattr(super(Dotty, self), key)

        if key not in self._data.keys():
            raise AttributeError(f"{repr(self)} has no attribute '{key}'")
        else:
            value = self._data[key]

        if isinstance(value, dict):
            return Dotty(value)
        return value

    def __repr__(self):
        return f'Dotty(data={self._data})'


# export dotty function
def dotty(data=None):
    if data is None:
        data = {}
    return Dotty(data)


# convert string to sorted function
def str2sort(raw):
    if not raw:
        # default sort
        return None
    # TODO: replace with safer operation
    return lambda p: eval(raw)


# convert string to filter function
def str2filter(raw):
    if not raw:
        # default filter
        return lambda _: True
    # TODO: replace with safer operation
    return lambda p: eval(raw)


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
