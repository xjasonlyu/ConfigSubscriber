#!/usr/bin/env python3

import re

from . import base
from . import utils
from . import exceptions

# NAME: n3ro
class N3RO(base.Node):

    def __init__(self, s):
        data = self._re_(s.upper())
        self.tag = data[0]
        self.name = data[1]
        self.region = utils.str2iso(data[1][data[1].find('→'):])
        self.code = data[2]
        self.flag = utils.iso2flag(self.region)

    def __str__(self):
        return f'{self.flag}{self.name}-{self.tag}-{self.code}'

    @staticmethod
    def _re_(s):
        s = s.replace('中继', 'RELAY')
        s = s.replace('专线', 'IPLC')
        s = s.replace(' → ', '→')
        if not re.match(r'\d\d', s[-2:]):
            s += ' ' + '00'
        r = re.compile(r'^([\w\-.]+?) (.+?) (\d+?)$')
        results = r.findall(s)
        if len(results) != 1:
            raise exceptions.ScriptError(f'regex mismatch {len(results)}')
        return results[0]


def nodalize(*args, **kwargs):
    return N3RO(*args, **kwargs)
