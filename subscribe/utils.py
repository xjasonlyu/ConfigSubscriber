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


# convert string to sorted function
def str2sort(raw):
    if not raw:
        # default sort
        return None
    # TODO: replace with safer operation
    return lambda p: eval(raw)
