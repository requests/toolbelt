# -*- coding: utf-8 -*-
import requests
import unittest

from requests_toolbelt.adapters import Pkcs12Adapter
from . import get_betamax

class TestPkcs12Adapter(unittest.TestCase):
    """Tests a simple requests.get() call using a .p12 cert.
    """
    def setUp(self):
        adapter = Pkcs12Adapter(max_retries=3, pkcs12_filename='./tests/certs/test_cert.p12', pkcs12_password='test')
        self.session = requests.Session()
        self.session.mount('https://', adapter)
        self.recorder = get_betamax(self.session)

    def test_pkcs12(self):
        with self.recorder.use_cassette('test_pkcs12_adapter'):
            r = self.session.get('https://pkiprojecttest01.dev.labs.internal/', verify=False)
            assert r.status_code == 200
            assert r.text