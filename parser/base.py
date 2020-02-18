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

    def __init__(self, s, *args, **kwargs):
        self._s = s

    def __str__(self):
        return self._s


def nodalize(*args, **kwargs):
    return Node(*args, **kwargs)
