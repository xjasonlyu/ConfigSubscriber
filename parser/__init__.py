#!/usr/bin/env python3

import re
import os
from os import path
from importlib import import_module

# builtin packages
from . import base
from . import utils


class Map:

    def __init__(self):
        files = (path.basename(f) for f in os.listdir(path.dirname(__file__)))
        modules = filter(lambda f: re.match(r'_[a-zA-Z0-9]+\.py', f), files)
        # import modules & convert to dict
        self._modules = dict([(m[1:-3].upper(), import_module('.'+m[:-3], __name__)) for m in modules])

    @staticmethod
    def _exception_wrapper(nodalize):
        # return base if error occurred
        def _wrapper(name):
            try:
                return nodalize(name)
            except:
                return base.nodalize(name)
        return _wrapper

    def __getitem__(self, key):
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
