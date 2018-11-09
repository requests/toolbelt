# -*- coding: utf-8 -*-
"""
requests_toolbelt.ssl_context_adapter
=====================================

This file contains an implementation of the SSLContextAdapter.

It requires a version of requests >= 2.4.0.
"""

import requests
from requests.adapters import HTTPAdapter


class SSLContextAdapter(HTTPAdapter):
    """
    An adapter that lets the user inject a custom SSL context for all
    requests made through it.

    The SSL context will simply be passed through to urllib3, which
    causes it to skip creation of its own context.

    Note that the SSLContext is not persisted when pickling - this is on
    purpose.
    So, after unpickling the SSLContextAdapter will behave like an
    HTTPAdapter until a new SSLContext is set.

    Example usage:

    .. code-block:: python

        import requests
        from ssl import create_default_context
        from requests import Session
        from requests_toolbelt.adapters.ssl_context import SSLContextAdapter

        s = Session()
        s.mount('https://', SSLContextAdapter(ssl_context=create_default_context()))
    """

    def __init__(self, **kwargs):
        self.ssl_context = None
        if 'ssl_context' in kwargs:
            self.ssl_context = kwargs['ssl_context']
            del kwargs['ssl_context']

        super(SSLContextAdapter, self).__init__(**kwargs)

    def __setstate__(self, state):
        # SSLContext objects aren't picklable and shouldn't be persisted anyway
        self.ssl_context = None
        super(SSLContextAdapter, self).__setstate__(state)

    def init_poolmanager(self, *args, **kwargs):
        if requests.__build__ >= 0x020400:
            if 'ssl_context' not in kwargs:
                kwargs['ssl_context'] = self.ssl_context
        super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)
