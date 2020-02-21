#!/usr/bin/env python3

import re
import requests


# simple url fetcher
def fetch_url(url: str, timeout: int = 5, allow_redirects: bool = True) -> str:
    # process URL
    if not re.match('(http|https|file)://', url):
        url = 'http://' + url
    # file protocol
    if url.startswith('file://'):
        url = url[7:]
        with open(url, 'r') as f:
            return f.read()
    # request headers
    headers = {
        # fake User-Agent
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
    # fetch rules via url
    def fetch_rules():
        for rules in (raw.splitlines() for raw in map(fetch_url, urls)):
            yield from rules

    for rule in fetch_rules():
        # strip whitespace
        rule = rule.strip()
        # ignore empty line or comment
        if not rule or rule.startswith('#'):
            continue

        _rule = [i.strip() for i in rule.split(',')]
        # set values
        if len(_rule) == 2:
            _type, _value, _attr = *_rule, ''
        elif len(_rule) == 3:
            _type, _value, _attr = _rule
        elif len(_rule) == 4:
            _type, _value, _policy, _attr = _rule
        else:
            # syntax error, ignore
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
