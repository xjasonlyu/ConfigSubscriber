#!/usr/bin/env python3

import re
import requests


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


# simple curl in python version
def curl(url: str, timeout: int = None, allow_redirects: bool = False) -> str:
    # process URL
    if not re.match('(http|https|file)://', url):
        url = 'http://' + url
    # file protocol
    if url.startswith('file://'):
        url = url[7:]
        with open(url, 'r') as f:
            return f.read()
    # curl headers
    headers = {
        'User-Agent': 'curl',
        'Accept': '*/*'
    }
    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
    r.raise_for_status()
    return r.text


# convert string to filter function
def str2filter(raw):
    if not raw:
        # default filter
        return lambda _: True
    # TODO: replace with safer operation
    return lambda p: eval(raw)


# convert string to sorted function
def str2sort(raw):
    if not raw:
        # default sort
        return None
    # TODO: replace with safer operation
    return lambda p: eval(raw)


# Generator
# convert Surge rules to Clash rules
def surge2clash(*urls):
    t = ('DOMAIN', 'DOMAIN-KEYWORD', 'DOMAIN-SUFFIX', 'IP-CIDR', 'GEOIP')
    m = {'SRC-IP': 'SRC-IP-CIDR', 'DEST-PORT': 'DST-PORT', 'IN-PORT': 'SRC-PORT'}
    # fetch rules
    rules = '\n'.join(curl(url, timeout=5, allow_redirects=True) for url in urls)

    for rule in rules.splitlines():
        # ignore empty line or comment
        if not rule or rule.startswith('#'):
            continue

        _rule = [i.strip() for i in rule.split(',')]
        if len(_rule) == 2:
            _rule.append('')

        # set values
        if len(_rule) == 3:
            _type, _value, _attr = _rule
        elif len(_rule) == 4:
            _type, _value, _policy, _attr = _rule
        else:
            # maybe an error, ignore
            continue

        # concat
        if _type in t:
            _data = f'{_type},{_value},{{}}'
        # replace
        elif _type in m:
            _data = f'{m[_type]},{_value},{{}}'
        else:
            continue

        # clash only support 'no-resolve' param
        if _attr == 'no-resolve':
            yield f'{_data},{_attr}'
        else:
            yield _data
