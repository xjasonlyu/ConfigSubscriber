#!/usr/bin/env python3

from . import utils


class Node:

    # Base fields
    tag = ''
    name = ''
    code = ''
    flag = ''
    rate = 1.0
    region = ''

    def __init__(self, name, *args, **kwargs):
        self.name = name

    def __iter__(self):
        for key in self.__dict__:
            if not key.startswith('_'):
                value = self.__dict__[key]
                if value is None or type(value) in utils.__types__:
                    yield (key, value)

    def __str__(self):
        return self.name


def nodalize(*args, **kwargs):
    return Node(*args, **kwargs)
