#!/usr/bin/env python3

from . import policy
from . import subscribe

__plugins__ = {'/subscribe/<client>': subscribe.subscribe}
