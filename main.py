#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse

import subscribe
from werkzeug.serving import run_simple


def parse_arguments():
    parser = argparse.ArgumentParser(prog='subscribe')

    # default config path
    cfg = os.path.join(os.getcwd(), 'config')

    parser.add_argument('-c', '--config', type=str, default=cfg,
                        help='config directory [Default=./config]')
    parser.add_argument('-b', '--bind', type=str, default='127.0.0.1',
                        help='host to serve [Default=127.0.0.1]')
    parser.add_argument('-p', '--port', type=int, default=9000,
                        help='port to serve [Default=9000]')
    parser.add_argument('--debug', action='store_true',
                        help='enable debug mode')
    parser.add_argument('--version', action='version',
                        version='%(prog)s v' + subscribe.version)

    args = parser.parse_args()

    # Normalize the path
    args.config = os.path.abspath(args.config)

    return args


def main():
    args = parse_arguments()
    subscribe.init(args.config)

    if args.debug:
        subscribe.app.debug = True

    run_simple(args.bind, args.port,
               subscribe.app, threaded=True,
               use_debugger=args.debug, use_reloader=args.debug,
               )


if __name__ == '__main__':
    main()
