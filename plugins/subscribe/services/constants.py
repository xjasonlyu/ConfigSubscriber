#!/usr/bin/env python3


class ScriptError(Exception):
    pass


class Node:

    tag = ''
    name = ''
    code = ''
    flag = ''
    rate = 1.0
    region = ''

    def __init__(self, *args, **kwargs):
        pass
