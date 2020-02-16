#!/usr/bin/env python3

import re

AUTH = ''

LINK = ''

SERVICE = 'N3RO'

TEMPLATE = {
    0: 'clash.yaml',
    1: 'surge.conf',
}

PROXIES_FILTER = lambda p: 1 if p.node.tag in ('IPLC', 'RELAY') else 0

# AUTO policy
POLICIES_FILTER = lambda p: 1 if p.node.tag == 'IPLC' and re.search('上|深|广', p.name) else 0

NAMES = 'MANUAL'

POLICIES_ARGS = (
    {'region': '',   'name': 'MANUAL'},
)
