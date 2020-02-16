#!/usr/bin/env python3


class Node:

    tag = ''
    name = ''
    code = ''
    flag = ''
    rate = 1.0
    region = ''

    def __init__(self, *args, **kwargs):
        pass


# builtin packages
from . import utils
from . import exceptions

# services
from . import n3ro
