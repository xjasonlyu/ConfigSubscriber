#!/usr/bin/env python3

from . import base
from . import utils


# NAME: n3ro
class N3RO(base.Node):

    def __init__(self, name):
        super(N3RO, self).__init__(name)

        data = self._process_(name.upper())
        self.net, self.name, self.code = data
        self.iso = utils.find_iso(data[1][data[1].find('→'):])
        self.flag = utils.iso2flag(self.iso)

    def __str__(self):
        return f'{self.flag}{self.name}-{self.net}-{self.code}'

    @staticmethod
    def _process_(s):
        s = s.replace('中继', 'RELAY')
        s = s.replace('专线', 'IPLC')
        s = s.replace(' → ', '→')
        return s.split()


def nodalize(*args, **kwargs):
    return N3RO(*args, **kwargs)
