#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import app
from .utils import fetch_url


# Generator: convert Surge rules to Clash rules
@app.template_filter()
def surge2clash(policy, *urls):
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

        offset = rule.find('#')
        if offset > -1:
            # remove inline comment
            rule = rule[:offset]

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
            _data = f'{_type},{_value},{policy}'
        # replace
        elif _type in m:
            _data = f'{m[_type]},{_value},{policy}'
        else:
            continue

        # clash only support 'no-resolve' param
        if _attr == 'no-resolve':
            yield f'{_data},{_attr}'
        else:
            yield _data
