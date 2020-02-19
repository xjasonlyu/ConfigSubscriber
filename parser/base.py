#!/usr/bin/env python3

from . import utils


class Node:

    # Base fields
    iso = ''      # isocode: HK
    net = ''      # net: IPLC RELAY
    tag = ''      # tag: xxx
    attr = ''     # attr: xxx
    code = ''     # id: 01
    flag = ''     # emoji flag
    name = ''     # xxx
    rate = 1.0    # rate

    def __init__(self, name, *args, **kwargs):
        self._name = name

    def __str__(self):
        return self._name

    def __getattr__(self, key):
        return self.__dict__.get(key, '')

    def __gt__(self, other):
        return str(self) > str(other)


def nodalize(*args, **kwargs):
    return Node(*args, **kwargs)
