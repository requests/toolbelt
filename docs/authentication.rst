.. _authentication:

Authentication
==============

requests supports Basic Authentication and HTTP Digest Authentication by
default. There are also a number of third-party libraries for authentication
with:

- `OAuth <https://requests-oauthlib.readthedocs.org/en/latest/>`_

- `NTML <https://github.com/requests/request-ntlm>`_

- `Kerberos <https://github.com/requests/requests-kerberos>`_

The :mod:`requests_toolbelt.auth` provides extra authentication features in
addition to those. It provides the following authentication classes:

- :class:`requests_toolbelt.auth.GuessAuth`

- :class:`requests_toolbelt.auth.HTTPProxyDigestAuth`

GuessAuth
---------

The :class:`~requests_toolbelt.auth.GuessAuth` authentication class
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

.. autoclass:: requests_toolbelt.auth.GuessAuth


HTTPProxyDigestAuth
-------------------

The ``HTTPProxyDigestAuth`` use digest authentication between the client and
the proxy.

.. code-block:: python

    import requests
    from requests_toolbelt.auth import HTTPProxyDigestAuth


    proxies = {
        "http": "http://PROXYSERVER:PROXYPORT",
        "https": "https://PROXYSERVER:PROXYPORT",
    }
    url = "https://toolbelt.readthedocs.org/"
    auth = HTTPProxyDigestAuth("USERNAME", "PASSWORD")
    requests.get(url, proxies=proxies, auth=auth)

Program would raise error if the username or password is rejected by the proxy.

.. autoclass:: requests_toolbelt.auth.HTTPProxyDigestAuth
