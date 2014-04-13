# -*- coding: utf-8 -*-
"""

requests_toolbelt.auth_handler
==============================

This holds all of the implementation details of the Authentication Handler.

"""

from requests.auth import AuthBase, HTTPBasicAuth
from requests.compat import urlparse


class AuthHandler(AuthBase):

    """

    The ``AuthHandler`` object takes a dictionary of domains paired with
    authentication strategies and will use this to determine which credentials
    to use when making a request. For example, you could do the following:

    .. code-block:: python

        from requests import HTTPDigestAuth
        from requests_toolbelt import AuthHandler

        import requests

        auth = AuthHandler({
            'api.github.com': ('sigmavirus24', 'fakepassword'),
            'example.com': HTTPDigestAuth('username', 'password')
        })

        r = requests.get('https://api.github.com/user', auth=auth)
        # => <Response [200]>
        r = requests.get('https://example.com/some/path', auth=auth)
        # => <Response [200]>

        s = requests.Session()
        s.auth = auth
        r = s.get('https://api.github.com/user')
        # => <Response [200]>

    """

    def __init__(self, strategies):
        self.strategies = dict(strategies)
        self._make_uniform()

    def __call__(self, request):
        auth = self.get_strategy_for(request.url)
        return auth(request)

    def __repr__(self):
        return '<AuthHandler({0!r})>'.format(self.strategies)

    def _make_uniform(self):
        existing_strategies = list(self.strategies.items())
        self.strategies = {}

        for (k, v) in existing_strategies:
            self.add_strategy(k, v)

    def add_strategy(self, domain, strategy):
        """Add a new domain and authentication strategy.

        :param str domain: The domain you wish to match against. For example:
            ``'api.github.com'``
        :param str strategy: The authentication strategy you wish to use for
            that domain. For example: ``('username', 'password')`` or
            ``requests.HTTPDigestAuth('username', 'password')``

        >>> a = AuthHandler({})
        >>> a.add_strategy('api.github.com', ('username', 'password'))

        """
        # Turn tuples into Basic Authentication objects
        if isinstance(strategy, tuple):
            strategy = HTTPBasicAuth(*strategy)

        self.strategies[domain.lower()] = strategy

    def get_strategy_for(self, url):
        """Retrieve the authentication strategy for a specified URL.

        :param str url: The full URL you will be making a request against. For
            example, ``'https://api.github.com/user'``
        :returns: Callable that adds authentication to a request.

        >>> import requests
        >>> a = AuthHandler({'example.com', ('foo', 'bar')})
        >>> strategy = a.get_strategy_for('http://example.com/example')
        >>> isinstance(strategy, requests.auth.HTTPBasicAuth)
        True

        """
        parsed = urlparse(url)
        return self.strategies.get(parsed.netloc.lower(), NullAuthStrategy())

    def remove_strategy(self, domain):
        """Remove the domain and strategy from the collection of strategies.

        :param str domain: The domain you wish remove. For example,
            ``'api.github.com'``.

        >>> a = AuthHandler({'example.com', ('foo', 'bar')})
        >>> a.remove_strategy('example.com')
        >>> a.strategies
        {}

        """
        domain = domain.lower()
        if domain in self.strategies:
            del self.strategies[domain]


class NullAuthStrategy(AuthBase):
    def __repr__(self):
        return '<NullAuthStrategy>'

    def __call__(self, r):
        return r
