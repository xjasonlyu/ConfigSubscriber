#!/usr/bin/env python3

import base64
from functools import reduce


# Clients
CLASH = 0
SURGE = 1
OUTLINE = 2

__CLIENTS__ = {'clash': CLASH, 'surge': SURGE, 'outline': OUTLINE}

# Policies
SELECT = 0
AUTOURL = 1
FALLBACK = 2

__POLICIES__ = {'select': SELECT, 'auto-url': AUTOURL, 'fallback': FALLBACK}

# Proxy formatter mapping
PROXIES = {
    CLASH:   '  - {{ name: {proxy.node}, type: {proxy.type}, server: {proxy.server}, port: {proxy.port}, '
             'cipher: {proxy.cipher}, password: {proxy.password}, '
             'udp: {proxy.udp} }}',
    SURGE:   '{proxy.node} = {proxy.type}, {proxy.server}, {proxy.port}, '
             'encrypt-method={proxy.cipher}, password={proxy.password}, '
             'udp-relay={proxy.udp}',
    OUTLINE: 'ss://{code}@{proxy.server}:{proxy.port}',
}

# Policy formatter mapping
POLICES = {
    CLASH: {
        SELECT:   '  - {{ name: {name}, type: select, proxies: [{nodes}] }}',
        AUTOURL:  '  - {{ name: {name}, type: url-test, proxies: [{nodes}], '
                  'url: http://www.gstatic.com/generate_204, interval: 120 }}',
        FALLBACK: '  - {{ name: {name}, type: fallback, proxies: [{nodes}], '
                  'url: http://www.gstatic.com/generate_204, interval: 120 }}',
    },
    SURGE: {
        SELECT:   '{name} = select, {nodes}',
        AUTOURL:  '{name} = url-test, {nodes}, url=http://www.gstatic.com/generate_204, interval=120, tolerance=30',
        FALLBACK: '{name} = fallback, {nodes}, url=http://www.gstatic.com/generate_204, interval=120, tolerance=30',
    },
}

# Default filter (always return true)
FILTER = type


class Proxy:

    def __init__(self, proxy, node):
        self.name = proxy.get('name', '')
        self.type = proxy.get('type', '')
        self.server = proxy.get('server', '')
        self.port = proxy.get('port', 0)
        self.cipher = proxy.get('cipher', '')
        self.password = proxy.get('password', '')
        # default enable udp
        self.udp = 'true' if proxy.get('udp', True) else 'false'
        # Nodalize
        self.node = node(self.name)

    def serialize(self, client):
        if client == OUTLINE:
            code = base64.urlsafe_b64encode(f'{self.cipher}:{self.password}'.encode()).decode()
            return PROXIES[client].format(code=code, proxy=self)
        else:
            return PROXIES[client].format(proxy=self)


class Group:

    def __init__(self, raw_proxies, node, f=FILTER):

        proxies = list(filter(f, map(lambda i: Proxy(i, node), raw_proxies)))

        regions = dict()
        for p in proxies:
            if not regions.get(p.node.region):
                regions[p.node.region] = [p]
            else:
                regions[p.node.region].append(p)

        self.regions = regions

        self.proxies = proxies
        self.proxies.sort(key=lambda i: (i.node.tag, str(i.node)))

    def __len__(self):
        return len(self.proxies)

    def get_policy(self, region, name, client=CLASH, policy=SELECT, f=FILTER):
        if not region:
            proxies = self.proxies
        else:
            proxies = reduce(lambda x, y: x+y, [self.regions.get(r, []) for r in region.split('|')])

        if not proxies:
            return ''

        nodes = ', '.join([str(p.node) for p in filter(f, proxies)])

        return POLICES[client][policy].format(name=name, nodes=nodes)

    def get_proxies(self, client=CLASH):
        return '\n'.join([p.serialize(client) for p in self.proxies])
