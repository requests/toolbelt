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

    This allows requesting the IP address or CNAME directly via HTTPS without getting
    a "hostname doesn't match" exception.

    Example usage:

        >>> s.mount('https://', HostHeaderSSLAdapter())
        >>> s.get("https://93.184.216.34/", headers={"Host": "example.org"})
        >>> s.get("https://cname.example.org/", headers={"Host": "example.org"})
    """

    def send(self, request, **kwargs):
        # HTTP headers are case-insensitive (RFC 7230)
        # request.headers is a CaseInsensitiveDict
        host_header = request.headers.get('Host',None)

        connection_pool_kwargs = self.poolmanager.connection_pool_kw

        if request.url[:5] == "https" and host_header:
            connection_pool_kwargs["assert_hostname"] = host_header
            connection_pool_kwargs["server_hostname"] = host_header  # SNI
        else:
            # an assert_hostname from a previous request may have been left
            connection_pool_kwargs.pop("assert_hostname", None)
            connection_pool_kwargs.pop("server_hostname", None)  # SNI

        return super(HostHeaderSSLAdapter, self).send(request, **kwargs)
