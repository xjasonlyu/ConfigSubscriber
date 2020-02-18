#!/usr/bin/env python3

import json
import base64


# Filters
def FILTER(_): return True


# util to access dict with dot
class __DICT2CLASS__:

    def __init__(self, mapping: dict):
        self.mapping = mapping

    def __getattr__(self, key):
        return self.mapping.get(key)


class Proxy:

    def __init__(self, config, parse):
        self.name = config.get('name', '')
        self.type = config.get('type', '')
        self.server = config.get('server', '')
        self.port = config.get('port', 0)
        self.cipher = config.get('cipher', '')
        # ss
        self.password = config.get('password', '')
        # default enable udp
        self.udp = json.dumps(config.get('udp', True))
        # TODO: support vmess & other protocols
        # self.uuid = config.get('uuid', '')
        # self.alterId = config.get('alterId', '')
        # self.username = config.get('username', '')
        # # default disable tls
        # self.tls = json.dumps(config.get('tls', True))
        #
        # Nodalize
        self.node = parse(self.name)

    def __iter__(self):
        for key in self.__dict__:
            if key.startswith('__'):
                continue
            if key == 'node':
                yield (key, dict(self.node))
            else:
                yield (key, getattr(self, key))


class ProxyGroup:

    def __init__(self, raw_proxies, parse):

        proxies = list(map(lambda p: Proxy(p, parse), raw_proxies))

        regions = {}
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

    def __iter__(self):
        for proxy in self.proxies:
            yield proxy

    def get_proxies(self, f=FILTER):
        return filter(f, self.proxies)

    def get_policies(self, f=FILTER, **kwargs):
        # set attrs to empty dict if not set
        kwargs['attrs'] = kwargs.get('attrs', {})
        # generate nodes field
        nodes = ', '.join((str(p.node) for p in filter(f, self.proxies)))
        # update nodes to kwargs
        kwargs.update(nodes=nodes)

        return __DICT2CLASS__(kwargs)
