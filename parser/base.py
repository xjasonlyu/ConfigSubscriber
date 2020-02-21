#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .utils import *


class Node:

    # Base fields 
    net = ''      # net: IPLC RELAY
    tag = ''      # tag: xxx
    attr = ''     # attr: xxx
    code = ''     # id: 01
    name = ''     # xxx
    rate = 1.0    # rate

    _iso = None      # iso code: HK
    _flag = None     # emoji flag
    _name = None     # original node name

    def __init__(self, name, *args, **kwargs):
        self._name = name

    def __str__(self):
        return f"{self.flag}{self._name.replace(' ', '-')}"

    def __getattr__(self, key):
        return self.__dict__.get(key, '')

    def __gt__(self, other):
        return str(self) > str(other)

    @property
    def iso(self):
        if self._iso is None:
            # try to find ISO code from name
            self._iso = find_iso(self._name, ignore=True)

        return self._iso

    @iso.setter
    def iso(self, iso):
        if self._iso == iso:
            return

        flag = iso2flag(iso)
        if flag:
            self._iso = iso
            self._flag = flag


    @property
    def flag(self):
        if self._flag is None:
            self._flag = iso2flag(self.iso)

        return self._flag

    @flag.setter
    def flag(self, flag):
        if self._flag == flag:
            return

        iso = flag2iso(value)
        if iso:
            self._iso = iso
            self._flag = flag


def nodalize(*args, **kwargs):
    return Node(*args, **kwargs)
