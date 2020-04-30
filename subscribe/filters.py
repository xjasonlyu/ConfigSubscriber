#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import app
from . import session
from .proxies import Policy
from .proxies import Proxy

import re
from collections import Mapping
from itertools import chain
from urllib.parse import urlparse

import yaml
from jinja2 import Template
from orderedset import OrderedSet


# Turn object to dict
def _dict(obj):
    if isinstance(obj, (dict, Mapping)):
        return dict(obj)
    # export elements not startswith '_'
    _iterable = ((k, v) for k, v in obj.__dict__.items() if not k.startswith('_'))
    return dict(_iterable)


@app.template_filter('filter')
def _eval_filter(seq, key):
    if not key:
        key = True

    # builtin functions
    _builtins = {
        'regex_match': lambda exp, text: re.match(exp, text),
        'regex_search': lambda exp, text: re.search(exp, text)
    }
    # Jinja2 template
    t = Template(f'{{% if {key} %}}{{{{ True }}}}{{% endif %}}')
    return (item for item in seq if t.render(**_builtins, **_dict(item)))


# Filter proxies with key
@app.template_filter('filter_proxies')
def _filter_proxies(proxies, key=None, attr='node'):
    return (getattr(proxy, attr) for proxy in _eval_filter(proxies, key))


# Simple url fetcher
@app.template_filter()
def fetch_url(url: str, timeout: int = 5, allow_redirects: bool = True) -> str:
    # process URL
    if not re.match('(http|https|file)://', url):
        url = 'http://' + url
    # file protocol
    if url.startswith('file://'):
        path = urlparse(url).path
        with open(path, 'r') as f:
            return f.read()
    # request headers
    headers = {
        'Accept': '*/*'
    }
    r = session.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
    r.raise_for_status()
    return r.text


@app.template_filter()
def get_proxies(text, parser):
    # TODO: support other kind configs
    # load from yaml text
    items = yaml.safe_load(text)
    raw_proxies = items.get('Proxy')
    # remove duplicate proxy via name
    raw_proxies_table = dict((proxy['name'], proxy) for proxy in raw_proxies)
    # proxy node parser
    return (Proxy(proxy, parser) for proxy in raw_proxies_table.values())


@app.template_filter()
def get_policies(text):
    # load from yaml text
    raw_policies = yaml.safe_load(text)
    #
    return map(Policy, raw_policies)


@app.template_filter()
def regex_match(text, expression):
    return re.match(expression, text)


@app.template_filter()
def regex_search(text, expression):
    return re.search(expression, text)


# Convert yaml to clash config
@app.template_filter('toclash')
def to_clash(obj, prefix='', suffix=''):
    # Proxy
    if isinstance(obj, Proxy):
        result = Template('{ name: {{node}}, type: {{type}}, server: {{server}}, port: {{port}}, '
                          'cipher: {{cipher}}, password: {{password}}, udp={{udp|lower}} }'
                          ).render(**_dict(obj))
    # ProxyGroup
    elif isinstance(obj, Policy):
        result = Template('{ name: {{name}}, type: {{type}}, proxies: [{{proxies|join(", ")}}]'
                          '{% for k,v in attrs.items() %}, {{k}}: {{v}}{% endfor %} }'
                          ).render(**_dict(obj))
    else:
        result = str(obj)

    return prefix + result + suffix


# Convert yaml to surge config
@app.template_filter('tosurge')
def to_surge(obj, prefix='', suffix=''):
    # Proxy
    if isinstance(obj, Proxy):
        result = Template('{{node}} = {{type}}, {{server}}, {{port}}, encrypt-method={{cipher}}, '
                          'password={{password}}, udp-relay={{udp|lower}}'
                          ).render(**_dict(obj))
    # ProxyGroup
    elif isinstance(obj, Policy):
        result = Template('{{name}} = {{type}}, {{proxies|join(", ")}}'
                          '{% for k,v in attrs.items() %}, {{k}}={{v}}{% endfor %}'
                          ).render(**_dict(obj))
    else:
        result = str(obj)

    return prefix + result + suffix


# Generator: convert Surge rules to Clash rules
@app.template_filter('s2c')
def surge2clash(policy, *urls):
    t = ('DOMAIN', 'DOMAIN-KEYWORD', 'DOMAIN-SUFFIX', 'IP-CIDR', 'GEOIP')
    m = {'SRC-IP': 'SRC-IP-CIDR', 'DEST-PORT': 'DST-PORT', 'IN-PORT': 'SRC-PORT'}

    for rule in chain(*[raw.splitlines() for raw in map(fetch_url, urls)]):
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


# add absent rules
@app.template_filter('add_abs_rules')
def add_abs_rules(rule_text, *urls):
    new_rules = OrderedSet(rule_text.splitlines())
    for rule in chain(*[raw.splitlines() for raw in map(fetch_url, urls)]):
        # strip whitespace
        rule = rule.strip()
        # ignore empty line
        if not rule:
            continue
        # remove force-remote-dns option
        if rule.endswith(',force-remote-dns'):
            rule = rule[:-len(',force-remote-dns')]
        # add rule include comment
        new_rules.add(rule)
    return '\n'.join(new_rules)


# remove duplicate rules
@app.template_filter('rm_dup_rules')
def rm_dup_rules(rule_text, *urls):
    rule_set = OrderedSet()
    for rule in chain(*[raw.splitlines() for raw in map(fetch_url, urls)]):
        # strip whitespace
        rule = rule.strip()
        # ignore empty line or comment
        if not rule or rule.startswith('#'):
            continue
        rule_set.add(rule)
    return '\n'.join(rule for rule in rule_text.splitlines() if rule not in rule_set)
