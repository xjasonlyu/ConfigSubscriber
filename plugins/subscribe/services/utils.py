#!/usr/bin/env python3

import re
import requests
from os import path


# common region mapping
__region2iso__ = {
        '港': 'HK',
        '新': 'SG',
        '美': 'US',
        '圣': 'US',
        '洛': 'US',
        '台': 'TW',
        '韩': 'KR',
        '日': 'JP',
        '德': 'DE',
        '英': 'GB',
        '法': 'FR',
        '澳': 'AU',
        '俄': 'RU',
        '巴': 'BR',
    }


def str2iso(name, ignore=False):
    match = [__region2iso__[i] for i in name if i in __region2iso__]

    if len(match) == 1:
        return match[0]
    elif ignore:
        return
    elif len(match) == 0:
        raise Exception(f"no region detected: {name}")
    else:
        raise Exception(f"multiple region detected: {match}")


def iso2flag(iso: str) -> str:
    return flagize(f':{iso}:')


def flagize(text: str) -> str:
    def flag(code):
        points = [ord(x) + 127397 for x in code.upper()]
        return chr(points[0]) + chr(points[1])

    def flag_repl(match_obj):
        return flag(match_obj.group(1))

    return re.sub(':([a-zA-Z]{2}):', flag_repl, text)


def dflagize(text: str) -> str:
    def dflag(i):
        points = tuple(ord(x) - 127397 for x in i)
        return ':%c%c:' % points

    def dflag_repl(match_obj):
        return dflag(match_obj.group(0))

    regex = re.compile(u'([\U0001F1E6-\U0001F1FF]{2})', flags=re.UNICODE)
    return regex.sub(dflag_repl, text)


# simple curl in python version
def curl(url: str, timeout: int = None, allow_redirects: bool = False) -> bytes:
    # process URL
    if not re.match('(http|https|file)://', url):
        url = 'http://' + url
    # file protocol
    if url.startswith('file://'):
        url = url[7:]
        if not path.exists(url):
            return b''
        with open(url, 'rb') as f:
            return f.read()
    # curl headers
    headers = {
        'User-Agent': 'curl',
        'Accept': '*/*'
    }
    # requests session
    s = requests.Session()
    s.trust_env = False
    # requests
    try:
        r = s.get(url, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
        r.raise_for_status()
        return r.content
    except:
        return b''


def test():
    pass


if __name__ == '__main__':
    test()
