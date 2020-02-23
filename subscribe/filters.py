#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package Flask App
from . import app
from . import session

import re
import yaml
import requests
from jinja2 import Template
from collections import Mapping


class Proxy:

    def __init__(self, config, nodalize):
        # original name
        self.name = config.get('name', '')
        # only ss support yet
        self.type = config.get('type', '')
        self.server = config.get('server', '')
        self.port = config.get('port', 0)
        self.password = config.get('password', '')
        # default enable udp
        self.udp = config.get('udp-relay') or config.get('udp', True)
        # encrypt method or cipher
        self.cipher = config.get('encrypt-method') or config.get('cipher', '')
        # TODO: support vmess & other protocols
        # self.uuid = config.get('uuid', '')
        # self.alterId = config.get('alterId', '')
        # self.username = config.get('username', '')
        # # default disable tls
        # self.tls = json.dumps(config.get('tls', True))
        #
        # Nodalize
        # use node as name
        self.node = nodalize(self.name)

    def __str__(self):
        return self.name

    def __gt__(self, other):
        return str(self) > str(other)


class Policy:

    def __init__(self, config):
        # original config
        self._config = config
        # basic info
        self.name = config.get('name', '')
        self.type = config.get('type', '')
        self.proxies = config.get('proxies', '')
        # attributions
        self.attrs = {}
        # add attrs
        for key, value in config.items():
            if key in ('name', 'type', 'proxies'):
                continue
            self.attrs[key] = value

    def __str__(self):
        return self.name


# turn object to dict
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
    # Jinja template
    t = Template(f'{{% if {key} %}}{{{{ True }}}}{{% endif %}}')
    return (item for item in seq if t.render(**_builtins, **_dict(item)))


# filter proxies with key
@app.template_filter('filter_proxies')
def _filter_proxies(proxies, key=None, attr='node'):
    return (getattr(proxy, attr) for proxy in _eval_filter(proxies, key))


# simple url fetcher
@app.template_filter()
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
    # proxy node parser
    return (Proxy(proxy, parser) for proxy in raw_proxies)


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
