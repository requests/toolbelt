.. _authentication:

Authentication
==============

requests supports Basic Authentication and HTTP Digest Authentication by
default. There are also a number of third-party libraries for authentication
with:

- `OAuth <https://requests-oauthlib.readthedocs.org/en/latest/>`_

- `NTLM <https://github.com/requests/requests-ntlm>`_

- `Kerberos <https://github.com/requests/requests-kerberos>`_

The :mod:`requests_toolbelt.auth` provides extra authentication features in
addition to those. It provides the following authentication classes:

- :class:`requests_toolbelt.auth.guess.GuessAuth`

- :class:`requests_toolbelt.auth.http_proxy_digest.HTTPProxyDigestAuth`

- :class:`requests_toolbelt.auth.handler.AuthHandler`

AuthHandler
-----------

The :class:`~requests_toolbelt.auth.handler.AuthHandler` is a way of using a
single session with multiple websites that require authentication. If you know
what websites require a certain kind of authentication and what your
credentials are.

Take for example a session that needs to authenticate to GitHub's API and
GitLab's API, you would set up and use your
:class:`~requests_toolbelt.auth.handler.AuthHandler` like so:

.. code-block:: python

    import requests
    from requests_toolbelt.auth.handler import AuthHandler

    def gitlab_auth(request):
        request.headers['PRIVATE-TOKEN'] = 'asecrettoken'

    handler = AuthHandler({
        'https://api.github.com': ('sigmavirus24', 'apassword'),
        'https://gitlab.com': gitlab_auth,
    })

    session = requests.Session()
    session.auth = handler
    r = session.get('https://api.github.com/user')
    # assert r.ok
    r2 = session.get('https://gitlab.com/api/v3/projects')
    # assert r2.ok

.. note::

    You **must** provide both the scheme and domain for authentication. The
    :class:`~requests_toolbelt.auth.handler.AuthHandler` class will check both
    the scheme and host to ensure your data is not accidentally exposed.

.. autoclass:: requests_toolbelt.auth.handler.AuthHandler
    :members:

GuessAuth
---------

The :class:`~requests_toolbelt.auth.guess.GuessAuth` authentication class
automatically detects whether to use basic auth or digest auth:

.. code-block:: python

    import requests
    from requests_toolbelt.auth import GuessAuth

    requests.get('http://httpbin.org/basic-auth/user/passwd',
                 auth=GuessAuth('user', 'passwd'))
    requests.get('http://httpbin.org/digest-auth/auth/user/passwd',
                 auth=GuessAuth('user', 'passwd'))

Detection of the auth type is done via the ``WWW-Authenticate`` header sent by
the server. This requires an additional request in case of basic auth, as
usually basic auth is sent preemptively. If the server didn't explicitly
require authentication, no credentials are sent.

.. autoclass:: requests_toolbelt.auth.guess.GuessAuth


GuessProxyAuth
--------------

The :class:`~requests_toolbelt.auth.guess.GuessProxyAuth` handler will
automatically detect whether to use basic authentication or digest authentication
when authenticating to the provided proxy.

.. code-block:: python

    import requests
    from requests_toolbelt.auth.guess import GuessProxyAuth

    proxies = {
        "http": "http://PROXYSERVER:PROXYPORT",
        "https": "http://PROXYSERVER:PROXYPORT",
    }
    requests.get('http://httpbin.org/basic-auth/user/passwd',
                 auth=GuessProxyAuth('user', 'passwd', 'proxyusr', 'proxypass'),
                 proxies=proxies)
    requests.get('http://httpbin.org/digest-auth/auth/user/passwd',
                 auth=GuessProxyAuth('user', 'passwd', 'proxyusr', 'proxypass'),
                 proxies=proxies)

Detection of the auth type is done via the ``Proxy-Authenticate`` header sent by
the server. This requires an additional request in case of basic auth, as
usually basic auth is sent preemptively. If the server didn't explicitly
require authentication, no credentials are sent.

.. autoclass:: requests_toolbelt.auth.guess.GuessProxyAuth

HTTPProxyDigestAuth
-------------------

The ``HTTPProxyDigestAuth`` use digest authentication between the client and
the proxy.

.. code-block:: python

    import requests
    from requests_toolbelt.auth.http_proxy_digest import HTTPProxyDigestAuth


    proxies = {
        "http": "http://PROXYSERVER:PROXYPORT",
        "https": "https://PROXYSERVER:PROXYPORT",
    }
    url = "https://toolbelt.readthedocs.org/"
    auth = HTTPProxyDigestAuth("USERNAME", "PASSWORD")
    requests.get(url, proxies=proxies, auth=auth)

Program would raise error if the username or password is rejected by the proxy.

.. autoclass:: requests_toolbelt.auth.http_proxy_digest.HTTPProxyDigestAuth
