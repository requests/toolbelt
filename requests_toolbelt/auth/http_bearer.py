# -*- coding: utf-8 -*-
"""The module containing HTTPBearerAuth."""

from requests.auth import AuthBase


class HTTPBearerAuth(AuthBase):
    """HTTP Bearer Token Authentication
    """

    def __init__(self, token):
        self.token = token

    def __eq__(self, other):
        return self.token == getattr(other, 'token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r
