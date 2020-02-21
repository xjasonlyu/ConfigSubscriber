#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from . import base
from . import utils


# NAME: rixcloud
class RixCloud(base.Node):

    def __init__(self, name):
        super(RixCloud, self).__init__(name)

        self.iso, self.attr, self.net, self.code = self._process_(name.upper())

    def __str__(self):
        return f'{self.flag}{self.iso}-{self.attr}-{self.net}-{self.code}'

    @staticmethod
    def _process_(s: str) -> list:
        # special replacement
        if 'NETEASE' in s:
            raise Warning('ignore netease node')
        s = utils.replace_with_iso(s)
        #
        s = s.replace('中继', 'RELAY')
        s = s.replace('边缘', 'EDGE')
        #
        s = s.replace('标准 BGP', ' STD')
        s = s.replace('特殊 BGP', ' SPEC')
        s = s.replace('实验性 BGP', ' EXP')
        return s.split()


def nodalize(*args, **kwargs):
    return RixCloud(*args, **kwargs)
