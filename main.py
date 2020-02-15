#!/usr/bin/env python3

import os
import re
import logging
import importlib
from flask import Flask
from configparser import ConfigParser


# Global Flask Instance
app = Flask(__name__)

# Global Variables
cfg = ConfigParser()
cwd = os.path.dirname(__file__)


def init():
    cfg.read(os.path.join(cwd, 'config.ini'))

    # DEBUG & LOG
    app.debug = cfg.getboolean('common', 'debug', fallback=False)
    if not app.debug:
        log_file = cfg.get('common', 'log', fallback=None)
        log_level = getattr(logging, \
            cfg.get('common', 'loglevel', fallback='info').upper(), logging.INFO)
        if log_file:
            logging.basicConfig(
                filename=log_file,
                format='%(asctime)s %(levelname)s: %(message)s',
                level=log_level
            )

    # PLUGINS
    plugins = re.sub(',|:|;|\'|"', ' ', \
        cfg.get('plugins', 'name', fallback='')).split()
    for plugin in plugins:
        # import plugins
        p = '.'.join([ 'plugins', plugin ])
        m = importlib.import_module(p)
        # add each function to app url rules
        for u, f in m.__plugins__.items():
            app.add_url_rule(u, view_func=f)


init()


def main():
    # init flask app
    host = cfg.get('common', 'host', fallback='127.0.0.1')
    port = cfg.getint('common', 'port', fallback=8000)
    reloader = cfg.getboolean('common', 'reload', fallback=False)
    # start instance
    app.run(host=host, port=port, use_reloader=reloader)


if __name__ == "__main__":
    main()
