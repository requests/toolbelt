# -*- coding: utf-8 -*-
import betamax
import requests
import unittest

from requests_toolbelt import SSLAdapter


class TestSSLAdapter(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.session.mount('https://', SSLAdapter('SSLv3'))
        self.recorder = betamax.Betamax(
            self.session,
            cassette_library_dir='tests/cassettes')

    def test_klevas(self):
        with self.recorder.use_cassette('klevas_vu_lt_ssl3'):
            r = self.session.get('https://klevas.vu.lt/')
            assert r.status_code == 200
