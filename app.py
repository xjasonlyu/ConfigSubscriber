#!/usr/bin/env python3

import re
import logging
import importlib
from os import path
from flask import Flask
from configparser import ConfigParser


# Global Flask Instance
app = Flask(__name__)

# Global Variables
cwd = path.dirname(__file__)
cfg = ConfigParser()
cfg.read(path.join(cwd, 'config.ini'))


def init():
    # DEBUG & LOG
    app.debug = cfg.getboolean('common', 'debug', fallback=False)
    if not app.debug:
        log_file = cfg.get('common', 'log', fallback=None)
        log_level = cfg.get('common', 'loglevel', fallback='info').upper()
        if log_file or log_level not in ('NONE', 'SILENT'):
            handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=1024*1024*100, backupCount=5)
            handler.setLevel(getattr(logging, log_level, logging.INFO))
            handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'))
            app.logger.addHandler(handler)

    # PLUGINS
    plugins = re.sub(r',|:|;|\'|"', ' ',
                     cfg.get('common', 'plugins', fallback='')).split()
    for plugin in plugins:
        # import plugins
        p = '.'.join(['plugins', plugin])
        m = importlib.import_module(p)
        if not hasattr(m, '__plugins__'):
            app.logger.error(f'Invalid plugin package: {m.__name__}')
            continue
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
