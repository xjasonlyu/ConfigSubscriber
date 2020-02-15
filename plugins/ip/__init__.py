#!/usr/bin/env python3

from . import ip

__plugins__ = {
    '/ip': ip.get_ip,
    '/jsonip': ip.get_ip,
}
