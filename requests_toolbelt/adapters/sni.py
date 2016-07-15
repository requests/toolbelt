# -*- coding: utf-8 -*-
"""
requests_toolbelt.sni_adapter
=============================

This file contains an implementation of the SNIAdapter
"""

from requests.adapters import HTTPAdapter


class SNIAdapter(HTTPAdapter):
    """
    A HTTPS Adapter for Python Requests that sets the hostname for certificate
    verification based on the host header.

    This allows requesting the IP address directly via HTTPS without getting
    a "hostname doesn't match" exception.

    Example usage:

        >>> import requests
        >>> from requests_toolbelt import SNIAdapter
        >>> s = requests.Session()
        >>> s.mount('https://', SNIAdapter())
        >>> s.get("https://93.184.216.34", headers={"Host": "example.org"})

    """

    def send(self, request, **kwargs):

        # HTTP headers are case-insensitive (RFC 7230)
        host = None
        for header in request.headers:
            if header.lower() == "host":
                host = request.headers[header]
                break

        if host:
            self.poolmanager.connection_pool_kw["assert_hostname"] = host
        elif "assert_hostname" in self.poolmanager.connection_pool_kw:
            # an assert_hostname from a previous request may have been left
            del self.poolmanager.connection_pool_kw["assert_hostname"]

        return super(SNIAdapter, self).send(request, **kwargs)
