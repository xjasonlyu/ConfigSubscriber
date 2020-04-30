#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Package variables
from . import config

# Package modules
from .filters import fetch_url

# Python library
from urllib.parse import urljoin

# Flask modules
from markupsafe import escape
from flask import render_template
from flask import render_template_string

# Exceptions
from requests.exceptions import HTTPError


# serve local rule
def serve_local(rule):
    template_rule = f'ruleset/{escape(rule)}'
    return render_template(template_rule)


# serve remote rule
def serve_remote(rule):
    for remote in config['ruleset']['remotes']:
        # add slash to remote url
        if not remote.endswith('/'):
            remote += '/'
        # join remote url
        rule_url = urljoin(remote, escape(rule))
        try:
            text = fetch_url(rule_url)
            return render_template_string(text)
        except HTTPError:
            continue
