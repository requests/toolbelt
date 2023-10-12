# -*- coding: utf-8 -*-
import requests
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from requests_toolbelt.auth.http_bearer import HTTPBearerAuth
from . import get_betamax


class TestBearerAuth(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.recorder = get_betamax(self.session)

    def cassette(self):
        return self.recorder.use_cassette(
            'httpbin_bearer_auth',
            match_requests_on=['method', 'uri']
        )

    def test_bearer(self):
        with self.cassette():
            r = self.session.request(
                'GET', 'http://httpbin.org/bearer-auth/',
                auth=HTTPBearerAuth('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'))

        assert r.json() == {'authenticated': True, 'user': 'user'}
