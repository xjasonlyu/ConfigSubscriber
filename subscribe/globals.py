#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package Flask App
from . import app

from flask import abort
from datetime import datetime

# Directly add
app.add_template_global(abort)


# Formatted date
@app.template_global()
def date():
    return datetime.now().strftime('%Y%m%d')
