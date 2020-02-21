#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests


# simple url fetcher
def fetch_url(url: str, timeout: int = 5, allow_redirects: bool = True) -> str:
    # process URL
    if not re.match('(http|https|file)://', url):
        url = 'http://' + url
    # file protocol
    if url.startswith('file://'):
        url = url[7:]
        with open(url, 'r') as f:
            return f.read()
    # request headers
    headers = {
        'Accept': '*/*'
    }
    r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
    r.raise_for_status()
    return r.text


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
