# -*- coding: utf-8 -*-
import requests
import unittest
import pytest

from OpenSSL.crypto import load_pkcs12
from cryptography.hazmat.primitives.serialization import (Encoding, 
                                                          PrivateFormat,
                                                          NoEncryption,
                                                          BestAvailableEncryption)

from requests_toolbelt.adapters import X509Adapter
from . import get_betamax

REQUESTS_SUPPORTS_SSL_CONTEXT = requests.__build__ >= 0x021200

@pytest.mark.skipif(not REQUESTS_SUPPORTS_SSL_CONTEXT,
                    reason="Requires Requests v2.12.0 or later")
class TestX509AdapterAdapter(unittest.TestCase):
    """Tests a simple requests.get() call using a .p12 cert.
    """
    def setUp(self):
        self.session = requests.Session()
        self.recorder = get_betamax(self.session)

    def test_x509_pem(self):
        with self.recorder.use_cassette('test_x509_adapter'):
            with open('./tests/certs/test_cert.p12', 'rb') as pkcs12_file:
                pkcs12_data = pkcs12_file.read()

            pkcs12_password_bytes = "test".encode('utf8')

            p12 = load_pkcs12(pkcs12_data, pkcs12_password_bytes)
            cert_bytes = p12.get_certificate().to_cryptography().public_bytes(Encoding.PEM)
            pk_bytes = p12.get_privatekey().\
                           to_cryptography_key().\
                           private_bytes(Encoding.PEM, PrivateFormat.PKCS8, 
                                         BestAvailableEncryption(pkcs12_password_bytes))

            adapter = X509Adapter(max_retries=3, cert_bytes=cert_bytes, 
                                  pk_bytes=pk_bytes, password=pkcs12_password_bytes)
            self.session.mount('https://', adapter)

            r = self.session.get('https://pkiprojecttest01.dev.labs.internal/', verify=False)
            assert r.status_code == 200
            assert r.text

    def test_x509_der(self):
        with self.recorder.use_cassette('test_x509_adapter'):
            with open('./tests/certs/test_cert.p12', 'rb') as pkcs12_file:
                pkcs12_data = pkcs12_file.read()

            pkcs12_password_bytes = "test".encode('utf8')

            p12 = load_pkcs12(pkcs12_data, pkcs12_password_bytes)
            cert_bytes = p12.get_certificate().to_cryptography().public_bytes(Encoding.DER)
            # pyo_der_cert = PyoP12.get_certificate().to_cryptography().public_bytes(Encoding.DER)
            pk_bytes = p12.get_privatekey().to_cryptography_key().private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
            # pyo_der_key = PyoP12.get_privatekey().to_cryptography_key().private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
            adapter = X509Adapter(max_retries=3, cert_bytes=cert_bytes, pk_bytes=pk_bytes, encoding=Encoding.DER)
            self.session.mount('https://', adapter)

            r = self.session.get('https://pkiprojecttest01.dev.labs.internal/', verify=False)
            assert r.status_code == 200
            assert r.text        