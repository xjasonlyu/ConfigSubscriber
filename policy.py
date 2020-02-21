#!/usr/bin/env python3


class Proxy:

    def __init__(self, config, nodalize):
        self.name = config.get('name', '')
        self.type = config.get('type', '')
        self.server = config.get('server', '')
        self.port = config.get('port', 0)
        self.cipher = config.get('cipher', '')
        # ss
        self.password = config.get('password', '')
        # default enable udp
        self.udp = config.get('udp', True)
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


class ProxyGroup:

    def __init__(self, raw_proxies, f, nodalize, sort=None):

        proxies = map(lambda proxy: Proxy(proxy, nodalize), raw_proxies)

        self.proxies = sorted(filter(f, proxies), key=sort)

    def __len__(self):
        return len(self.proxies)

    def get_policy(self, f, **kwargs):
        # generate nodes field
        nodes = ', '.join((str(p.node) for p in filter(f, self.proxies)))
        # set default for attrs
        kwargs.setdefault('attrs', {})
        # update nodes to kwargs
        kwargs.update(nodes=nodes)
        return kwargs
