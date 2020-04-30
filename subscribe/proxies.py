#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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
