#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# common region mapping
__str2iso__ = {
    '中': 'CN',
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
    '意': 'IT',
    '俄': 'RU',
    '巴': 'BR',
    '荷': 'NL',
    '印': 'IN',
}

# Chinese region name to ISO
__region2iso__ = {
    '中国': 'CN',
    '香港': 'HK',
    '澳门': 'MO',
    '台湾': 'TW',
    '日本': 'JP',
    '美国': 'US',
    '韩国': 'KR',
    '英国': 'GB',
    '法国': 'FR',
    '荷兰': 'NL',
    '巴西': 'BR',
    '印度': 'IN',
    '意大利': 'IT',
    '俄罗斯': 'RU',
    '新加坡': 'SG',
}


def replace_with_iso(name: str) -> str:
    for country, iso_code in __region2iso__.items():
        if country in name:
            name = name.replace(country, iso_code)
    return name


def find_iso(name: str, ignore: bool = False) -> str:
    match = [__str2iso__[i] for i in name if i in __str2iso__]

    if len(match) == 1:
        return match[0]
    elif ignore:
        return ''
    elif len(match) == 0:
        raise Warning(f'no region detected')
    else:
        raise Warning(f'multiple region detected')


def iso2flag(iso: str) -> str:
    if len(iso) != 2:
        return ''

    flag = flagize(f':{iso}:')

    if flag.startswith(':'):
        # flagize failed
        return ''
    return flag


def flag2iso(flag: str) -> str:
    if len(flag) != 2:
        return ''

    iso = dflagize(flag)

    if iso == flag:
        # dflagize failed
        return ''
    return iso.strip(':')


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
