# -*- coding: utf-8 -*-
"""A Pkcs12Adapter for use with the requests library.

This file contains an implementation of the Pkcs12Adapter that will
allow users to authenticate a request using a .p12/.pfx certificate
without needing to decrypt it to a .pem file

"""
from __future__ import division, print_function, unicode_literals

from OpenSSL.crypto import load_pkcs12
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.contrib.pyopenssl import PyOpenSSLContext
try:
    from ssl import PROTOCOL_TLS as PROTOCOL
except ImportError:
    from ssl import PROTOCOL_SSLv23 as PROTOCOL


class Pkcs12Adapter(HTTPAdapter):
    r"""Adapter for use with PKCS12 certificates.

    Provides an interface for Requests sessions to contact HTTPS urls and
    authenticate  with a PKCS 12 cert by implementing the Transport Adapter
    interface. This class will need to be manually instantiated and mounted
    to the session

    :param pool_connections: The number of urllib3 connection pools to
           cache.
    :param pool_maxsize: The maximum number of connections to save in the
            pool.
    :param max_retries: The maximum number of retries each connection
        should attempt. Note, this applies only to failed DNS lookups,
        socket connections and connection timeouts, never to requests where
        data has made it to the server. By default, Requests does not retry
        failed connections. If you need granular control over the
        conditions under which we retry a request, import urllib3's
        ``Retry`` class and pass that instead.
    :param pool_block: Whether the connection pool should block for
            connections.

    :param \**kwargs:
        see below

    :Keyword Arguments:
        * *pkcs12_data* (``bytes``) -- bytes object containing contents of a
            standard .p12 file as defined in RFC 7292.  Incompatible with
            ``pkcs12_filename``.
        * *pkcs12_filename* (``string``) -- path to a standard .p12 file as
            defined in RFC 7292. Incompatible with ``pkcs12_data``.
        * *pkcs12_password* (``string`` or ``bytes``) -- string or utf8 encoded
            bytes containing the passphrase used for the .p12 file.

    Usage::

      >>> import requests
      >>> s = requests.Session()
      >>> a = requests.adapters.Pkcs12Adapter(max_retries=3,
                pkcs12_filename='...', pkcs_password='...')
      >>> s.mount('https://', a)
    """

    def __init__(self, *args, **kwargs):
        _pkcs12_data = None
        _pkcs12_password_bytes = None
        pkcs12_data = kwargs.pop('pkcs12_data', None)
        pkcs12_filename = kwargs.pop('pkcs12_filename', None)
        pkcs12_password = kwargs.pop('pkcs12_password', None)
        if pkcs12_data is None and pkcs12_filename is None:
            raise ValueError('Both arguments "pkcs12_data" and'
                             ' "pkcs12_filename" are missing')
        if pkcs12_data is not None and pkcs12_filename is not None:
            raise ValueError('Argument "pkcs12_data" conflicts with'
                             ' "pkcs12_filename"')
        if pkcs12_password is None:
            raise ValueError('Argument "pkcs12_password" is missing')
        if pkcs12_filename is not None:
            with open(pkcs12_filename, 'rb') as pkcs12_file:
                _pkcs12_data = pkcs12_file.read()
        else:
            _pkcs12_data = pkcs12_data
        if isinstance(pkcs12_password, bytes):
            _pkcs12_password_bytes = pkcs12_password
        else:
            _pkcs12_password_bytes = pkcs12_password.encode('utf8')
        if _pkcs12_data and _pkcs12_password_bytes:
            self.ssl_context = create_ssl_context(_pkcs12_data,
                                                  _pkcs12_password_bytes)
        else:
            raise ValueError('Insufficient data to create SSL Context')

        super(Pkcs12Adapter, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        return super(Pkcs12Adapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        if self.ssl_context:
            kwargs['ssl_context'] = self.ssl_context
        return super(Pkcs12Adapter, self).proxy_manager_for(*args, **kwargs)


def check_cert_not_after(cert):
    """Verify that the supplied client cert is not expired."""
    cert_not_after = datetime.strptime(cert.get_notAfter().decode('ascii'),
                                       '%Y%m%d%H%M%SZ')
    if cert_not_after < datetime.utcnow():
        raise ValueError('Client certificate expired: Not After: '
                         '{cert_not_after:%Y-%m-%d %H:%M:%SZ}'
                         .format(**locals()))


def create_ssl_context(pkcs12_data, pkcs12_password_bytes):
    """Create an SSL Context with the supplied cert/password.

    :param pkcs12_data array of bytes containing the .p12 cert
    :param pkcs12_password_bytes utf8 encoded passphrase to use
            with the supplied cert
    """
    p12 = load_pkcs12(pkcs12_data, pkcs12_password_bytes)
    cert = p12.get_certificate()
    check_cert_not_after(cert)
    ssl_context = PyOpenSSLContext(PROTOCOL)
    ssl_context._ctx.use_certificate(cert)
    ssl_context._ctx.use_privatekey(p12.get_privatekey())
    return ssl_context
