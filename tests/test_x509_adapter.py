# -*- coding: utf-8 -*-
import requests
import unittest
import pytest

try:
    from OpenSSL.crypto import load_pkcs12
except ImportError:
    PYOPENSSL_AVAILABLE = False
else:
    PYOPENSSL_AVAILABLE = True
    from requests_toolbelt.adapters.x509 import X509Adapter
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PrivateFormat,
        NoEncryption,
        BestAvailableEncryption
    )

from requests_toolbelt import exceptions as exc
from . import get_betamax

REQUESTS_SUPPORTS_SSL_CONTEXT = requests.__build__ >= 0x021200


class TestX509Adapter(unittest.TestCase):
    """Tests a simple requests.get() call using a .p12 cert.
    """
    def setUp(self):
        with open('./tests/certs/test_cert.p12', 'rb') as pkcs12_file:
            self.pkcs12_data = pkcs12_file.read()

        self.pkcs12_password_bytes = "test".encode('utf8')
        self.session = requests.Session()

    @pytest.mark.skipif(not REQUESTS_SUPPORTS_SSL_CONTEXT,
                    reason="Requires Requests v2.12.0 or later")
    @pytest.mark.skipif(not PYOPENSSL_AVAILABLE,
                    reason="Requires OpenSSL")
    def test_x509_pem(self):
        p12 = load_pkcs12(self.pkcs12_data, self.pkcs12_password_bytes)
        cert_bytes = p12.get_certificate().to_cryptography().public_bytes(Encoding.PEM)
        pk_bytes = p12.get_privatekey().\
                       to_cryptography_key().\
                       private_bytes(Encoding.PEM, PrivateFormat.PKCS8,
                                     BestAvailableEncryption(self.pkcs12_password_bytes))

        adapter = X509Adapter(max_retries=3, cert_bytes=cert_bytes,
                              pk_bytes=pk_bytes, password=self.pkcs12_password_bytes)
        self.session.mount('https://', adapter)
        recorder = get_betamax(self.session)
        with recorder.use_cassette('test_x509_adapter_pem'):
            r = self.session.get('https://pkiprojecttest01.dev.labs.internal/', verify=False)

        assert r.status_code == 200
        assert r.text

    @pytest.mark.skipif(not REQUESTS_SUPPORTS_SSL_CONTEXT,
                    reason="Requires Requests v2.12.0 or later")
    @pytest.mark.skipif(not PYOPENSSL_AVAILABLE,
                    reason="Requires OpenSSL")
    def test_x509_der(self):
        p12 = load_pkcs12(self.pkcs12_data, self.pkcs12_password_bytes)
        cert_bytes = p12.get_certificate().to_cryptography().public_bytes(Encoding.DER)
        pk_bytes = p12.get_privatekey().to_cryptography_key().private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
        adapter = X509Adapter(max_retries=3, cert_bytes=cert_bytes, pk_bytes=pk_bytes, encoding=Encoding.DER)
        self.session.mount('https://', adapter)
        recorder = get_betamax(self.session)
        with recorder.use_cassette('test_x509_adapter_der'):
            r = self.session.get('https://pkiprojecttest01.dev.labs.internal/', verify=False)

        assert r.status_code == 200
        assert r.text

    @pytest.mark.skipif(REQUESTS_SUPPORTS_SSL_CONTEXT, reason="Will not raise exc")
    def test_requires_new_enough_requests(self):
        with pytest.raises(exc.VersionMismatchError):
            X509Adapter()
