# -*- coding: utf-8 -*-
"""
requests_toolbelt.source_adapter
================================

This file contains an implementation of the SourceAddressAdapter originally
demonstrated on the Requests GitHub page.
"""
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


class SourceAddressAdapter(HTTPAdapter):
    """
    A Source Address Adapter for Python Requests that enables you to choose the
    local address to bind to. This allows you to send your HTTP requests from a
    specific interface and IP address.

    Example usage:

    >>> import requests
    >>> from requests_toolbelt import SourceAddressAdapter
    >>> s = requests.Session()
    >>> s.mount('http://', SourceAddressAdapter('10.10.10.10'))
    """
    def __init__(self, source_address, **kwargs):
        self.source_address = source_address

        super(SourceAddressAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       source_address=self.source_address)
