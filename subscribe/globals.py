#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package Flask App
from . import app

from flask import abort
from datetime import datetime

# abort
app.add_template_global(abort)

# date
app.add_template_global(datetime.now().strftime, 'date')
