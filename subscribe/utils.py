#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re


# convert string to filter function
def str2filter(raw):
    if not raw:
        # default filter
        return lambda _: True
    # TODO: replace with safer operation
    return lambda p: eval(raw)
