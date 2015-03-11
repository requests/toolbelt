# -*- coding: utf-8 -*-
import requests
import unittest

from requests_toolbelt.auth.guess import GuessAuth
from . import get_betamax


class TestGuessAuth(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.recorder = get_betamax(self.session)

    def cassette(self, name):
        return self.recorder.use_cassette(
            'httpbin_guess_auth_' + name,
            match_requests_on=['method', 'uri', 'digest-auth']
        )

    def test_basic(self):
        with self.cassette('basic'):
            r = self.session.request(
                'GET', 'http://httpbin.org/basic-auth/user/passwd',
                auth=GuessAuth('user', 'passwd'))

        assert r.json() == {'authenticated': True, 'user': 'user'}

    def test_digest(self):
        with self.cassette('digest'):
            r = self.session.request(
                'GET', 'http://httpbin.org/digest-auth/auth/user/passwd',
                auth=GuessAuth('user', 'passwd'))

        assert r.json() == {'authenticated': True, 'user': 'user'}

    def test_no_auth(self):
        with self.cassette('none'):
            url = 'http://httpbin.org/get?a=1'
            r = self.session.request('GET', url,
                                     auth=GuessAuth('user', 'passwd'))

            j = r.json()
            assert j['args'] == {'a': '1'}
            assert j['url'] == url
            assert 'user' not in r.text
            assert 'passwd' not in r.text
