# -*- coding: utf-8 -*-
"""Test proxy digest authentication
"""

import unittest

import requests
from requests_toolbelt.auth import http_proxy_digest


class TestProxyDigestAuth(unittest.TestCase):
    def setUp(self):
        self.username = "username"
        self.password = "password"
        self.auth = http_proxy_digest.HTTPProxyDigestAuth(
            self.username, self.password
        )
        self.auth.last_nonce = "bH3FVAAAAAAg74rL3X8AAI3CyBAAAAAA"
        self.auth.chal = {
            'nonce': self.auth.last_nonce,
            'realm': 'testrealm@host.org',
            'qop': 'auth'
        }
        self.prepared_request = requests.Request(
            'GET',
            'http://host.org/index.html'
        ).prepare()

    def test_proxy_digest(self):
        """Test if it will generate Proxy-Authorization header
        when nonce presents.
        Digest authentication's correctness will not be tested here.
        """
        # prepared_request headers should be clear before calling auth
        assert not self.prepared_request.headers.get('Proxy-Authorization')
        self.auth(self.prepared_request)
        assert self.prepared_request.headers.get('Proxy-Authorization')

if __name__ == '__main__':
    unittest.main()
