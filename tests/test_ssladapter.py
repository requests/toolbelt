# -*- coding: utf-8 -*-
import requests
import unittest

from requests_toolbelt import SSLAdapter
from . import get_betamax


class TestSSLAdapter(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.session.mount('https://', SSLAdapter('SSLv3'))
        self.recorder = get_betamax(self.session)

    def test_klevas(self):
        with self.recorder.use_cassette('klevas_vu_lt_ssl3'):
            r = self.session.get('https://klevas.vu.lt/')
            assert r.status_code == 200
