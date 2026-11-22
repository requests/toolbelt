# -*- coding: utf-8 -*-
"""
requests_toolbelt.adapters.host_header_ssl
==========================================

This file contains an implementation of the HostHeaderSSLAdapter.
"""

from requests.adapters import HTTPAdapter


class HostHeaderSSLAdapter(HTTPAdapter):
    """
    A HTTPS Adapter for Python Requests that sets the hostname for certificate
    verification based on the Host header.

    This allows requesting the IP address directly via HTTPS without getting
    a "hostname doesn't match" exception.

    Example usage:

        >>> s.mount('https://', HostHeaderSSLAdapter())
        >>> s.get("https://93.184.216.34", headers={"Host": "example.org"})

    """

    __attrs__ = HTTPAdapter.__attrs__ + ['use_header', 'strip_header']

    def __init__(self, *args, **kwargs):
        self.use_header = kwargs.pop('use_header', 'Host')
        self.strip_header = kwargs.pop('strip_header', False)
        super(HostHeaderSSLAdapter, self).__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        # HTTP headers are case-insensitive (RFC 7230)
        host_header = None
        for header in request.headers:
            if header.lower() == self.use_header.lower():
                host_header = request.headers[header]
                if self.strip_header:
                    del request.headers[header]
                break

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        if host_header:
            connection_pool_kwargs["assert_hostname"] = host_header
            connection_pool_kwargs["server_hostname"] = host_header
        elif "assert_hostname" in connection_pool_kwargs:
            # an assert_hostname from a previous request may have been left
            connection_pool_kwargs.pop("assert_hostname", None)
            connection_pool_kwargs.pop("server_hostname", None)

        return super(HostHeaderSSLAdapter, self).send(request, **kwargs)
