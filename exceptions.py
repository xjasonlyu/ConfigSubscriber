#!/usr/bin/env python3


# Custom Exceptions
#
# Occurred when init failed
class InitError(Exception):
    pass


# 401 Unauthorized
class Unauthorized(Exception):
    pass


# 404 ClientNotFound
class ClientNotFound(Exception):
    pass
