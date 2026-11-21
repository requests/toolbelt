# -*- coding: utf-8 -*-
import requests
import unittest
import pytest

try:
    import OpenSSL
except ImportError:
    PYOPENSSL_AVAILABLE = False
else:
    PYOPENSSL_AVAILABLE = True
    from requests_toolbelt.adapters.x509 import X509Adapter
    from cryptography import x509
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PrivateFormat,
        BestAvailableEncryption,
        load_pem_private_key,
    )
    import trustme

from requests_toolbelt import exceptions as exc
from . import get_betamax

REQUESTS_SUPPORTS_SSL_CONTEXT = requests.__build__ >= 0x021200

pytestmark = pytest.mark.filterwarnings(
    "ignore:'urllib3.contrib.pyopenssl' module is deprecated:DeprecationWarning")


@pytest.mark.skipif(not PYOPENSSL_AVAILABLE, reason="Requires OpenSSL")
@pytest.mark.parametrize('build, version', [
    (0x021200, '2.12.0'),
    (0x022000, '2.20.0'),
    (requests.__build__, requests.__version__),
])
def test_missing_pyopenssl_context_reports_dependencies(monkeypatch,
                                                       build, version):
    from requests_toolbelt.adapters import x509 as adapter_module

    monkeypatch.setattr(requests, '__build__', build)
    monkeypatch.setattr(requests, '__version__', version)
    monkeypatch.setattr(adapter_module, 'PyOpenSSLContext', None)
    monkeypatch.setattr(X509Adapter, '_import_pyopensslcontext',
                        lambda self: None)

    with pytest.raises(exc.VersionMismatchError,
                       match='PyOpenSSLContext') as error:
        X509Adapter()

    message = str(error.value)
    assert version in message
    assert 'urllib3' in message
    assert 'pyOpenSSL' in message
    assert 'cryptography' in message


@pytest.mark.skipif(not PYOPENSSL_AVAILABLE, reason="Requires OpenSSL")
def test_old_requests_reports_version_requirement(monkeypatch):
    monkeypatch.setattr(requests, '__build__', 0x021100)
    monkeypatch.setattr(requests, '__version__', '2.11.0')

    with pytest.raises(exc.VersionMismatchError) as error:
        X509Adapter()

    assert 'requires at least Requests 2.12.0' in str(error.value)
    assert '2.11.0' in str(error.value)


@pytest.mark.skipif(not PYOPENSSL_AVAILABLE, reason="Requires OpenSSL")
def test_available_context_reaches_certificate_validation(monkeypatch):
    from requests_toolbelt.adapters import x509 as adapter_module

    monkeypatch.setattr(requests, '__build__', 0x021200)
    monkeypatch.setattr(adapter_module, 'PyOpenSSLContext', object())
    monkeypatch.setattr(X509Adapter, '_import_pyopensslcontext',
                        lambda self: None)

    with pytest.raises(ValueError, match='Invalid cert content'):
        X509Adapter()


class TestX509Adapter(unittest.TestCase):
    """Tests a simple requests.get() call using a .p12 cert.
    """
    def setUp(self):
        self.pkcs12_password_bytes = "test".encode('utf8')
        self.session = requests.Session()

    @pytest.mark.skipif(not REQUESTS_SUPPORTS_SSL_CONTEXT,
                        reason="Requires Requests v2.12.0 or later")
    @pytest.mark.skipif(not PYOPENSSL_AVAILABLE,
                        reason="Requires OpenSSL")
    def test_x509_pem(self):
        ca = trustme.CA()
        cert = ca.issue_cert(u'pkiprojecttest01.dev.labs.internal')
        cert_bytes = cert.cert_chain_pems[0].bytes()
        pk_bytes = cert.private_key_pem.bytes()

        adapter = X509Adapter(max_retries=3, cert_bytes=cert_bytes, pk_bytes=pk_bytes)
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
    def test_x509_der_and_password(self):
        ca = trustme.CA()
        cert = ca.issue_cert(u'pkiprojecttest01.dev.labs.internal')
        cert_bytes = x509.load_pem_x509_certificate(
            cert.cert_chain_pems[0].bytes()).public_bytes(Encoding.DER)
        pem_pk = load_pem_private_key(cert.private_key_pem.bytes(), password=None)
        pk_bytes = pem_pk.private_bytes(Encoding.DER, PrivateFormat.PKCS8,
                                        BestAvailableEncryption(self.pkcs12_password_bytes))

        adapter = X509Adapter(max_retries=3, cert_bytes=cert_bytes, pk_bytes=pk_bytes,
                              password=self.pkcs12_password_bytes, encoding=Encoding.DER)
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
