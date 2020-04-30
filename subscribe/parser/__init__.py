#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from importlib import import_module
from os import path

# builtin packages
from . import base


class Map:

    def __init__(self):
        files = (path.basename(f) for f in os.listdir(path.dirname(__file__)))
        modules = filter(lambda f: re.match(r'_[a-zA-Z0-9]+\.py', f), files)
        # import modules & convert to dict
        self._modules = dict([(m[1:-3].upper(), import_module(f'{__name__}.{m[:-3]}')) for m in modules])

    @staticmethod
    def _exception_wrapper(nodalize):
        # return base if error occurred
        def _wrapper(name):
            try:
                return nodalize(name)
            # capture all exceptions
            except:
                return base.nodalize(name)

        return _wrapper

    def __getitem__(self, key):
        # key is case-insensitive
        nodalize = getattr(self._modules[key.upper()], 'nodalize')
        return self._exception_wrapper(nodalize)

    def get(self, key, default=base.nodalize):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


_map_ = Map()


def get(*args, **kwargs):
    return _map_.get(*args, **kwargs)
