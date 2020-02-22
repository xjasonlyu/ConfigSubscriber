#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package Flask App
from . import app

import re
import yaml
import requests
from jinja2.utils import soft_unicode


class Proxy:

    def __init__(self, config, nodalize):
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
        self.node = nodalize(self.name)

    def __str__(self):
        return self.name

    def __gt__(self, other):
        return str(self) > str(other)


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
    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
    r.raise_for_status()
    return r.text


# Format sequence to string
@app.template_filter()
def format_seq(seq, fmt, concat='', **kwargs):
    # format & concat
    return concat.join(soft_unicode(fmt).format(text, **kwargs) for text in seq)


@app.template_filter()
def get_proxies(link, parser, f):
    def p(d):

        return d
    # fetch original subscription file
    text = fetch_url(link)
    # TODO: support other kind configs
    # load from yaml text
    items = yaml.safe_load(text)
    raw_proxies = items.get('Proxy')
    # proxy node parser
    proxies = (Proxy(proxy, parser) for proxy in raw_proxies)

    return filter(f, proxies)


@app.template_filter()
def get_policies(proxies, config):
    def get_policy(f, **kwargs):
        # generate nodes field
        nodes = ', '.join(str(p.node) for p in filter(f, proxies))
        # set default for attrs
        kwargs.setdefault('attrs', {})
        # update nodes to kwargs
        kwargs.update(proxies=nodes)
        return kwargs

    return [get_policy(**kwargs) for kwargs in config]


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
