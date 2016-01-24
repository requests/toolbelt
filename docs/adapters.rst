.. _adapters:

Transport Adapters
==================

The toolbelt comes with several different transport adapters for you to use
with requests. The transport adapters are all kept in
:mod:`requests_toolbelt.adapters` and include

- :class:`requests_toolbelt.adapters.appengine.AppEngineAdapter`

- :class:`requests_toolbelt.adapters.fingerprint.FingerprintAdapter`

- :class:`requests_toolbelt.adapters.socket_options.SocketOptionsAdapter`

- :class:`requests_toolbelt.adapters.socket_options.TCPKeepAliveAdapter`

- :class:`requests_toolbelt.adapters.source.SourceAddressAdapter`

- :class:`requests_toolbelt.adapters.ssl.SSLAdapter`

AppEngineAdapter
----------------

.. versionadded:: 0.6.0

As of version 2.10.0, Requests will be capable of supporting Google's App
Engine platform. In order to use Requests on GAE, however, you will need a
custome adapter found here as
:class:`~requests_toolbelt.adapters.appengine.AppEngineAdapter`. There are two
ways to take advantage of this support at the moment:

#. Using the :class:`~requests_toolbelt.adapters.appengine.AppEngineAdapter`
   like every other adapter, e.g.,

   .. code-block:: python

       import requests
       from requests_toolbelt.adapters import appengine

       s = requests.Session()
       s.mount('http://', appengine.AppEngineAdapter())
       s.mount('https://', appengine.AppEngineAdapter())

#. By monkey-patching requests to always use the provided adapter:

   .. code-block:: python

       import requests
       from requests_toolbelt.adapters import appengine

       appengine.monkeypatch()

.. autoclass:: requests_toolbelt.adapters.appengine.AppEngineAdapter

FingerprintAdapter
------------------

.. versionadded:: 0.4.0

By default, requests will validate a server's certificate to ensure a
connection is secure. In addition to this, the user can provide a fingerprint
of the certificate they're expecting to receive. Unfortunately, the requests
API does not support this fairly rare use-case. When a user needs this extra
validation, they should use the
:class:`~requests_toolbelt.adapters.fingerprint.FingerprintAdapter` class to
perform the validation.

.. autoclass:: requests_toolbelt.adapters.fingerprint.FingerprintAdapter

SSLAdapter
----------

The ``SSLAdapter`` is the canonical implementation of the adapter proposed on
Cory Benfield's blog, `here`_. This adapter allows the user to choose one of
the SSL/TLS protocols made available in Python's ``ssl`` module for outgoing
HTTPS connections.

In principle, this shouldn't be necessary: compliant SSL servers should be able
to negotiate the required SSL version. In practice there have been bugs in some
versions of OpenSSL that mean that this negotiation doesn't go as planned. It
can be useful to be able to simply plug in a Transport Adapter that can paste
over the problem.

For example, suppose you're having difficulty with the server that provides TLS
for GitHub. You can work around it by using the following code::

    from requests_toolbelt.adapters.ssl import SSLAdapter

    import requests
    import ssl

    s = requests.Session()
    s.mount('https://github.com/', SSLAdapter(ssl.PROTOCOL_TLSv1))

Any future requests to GitHub made through that adapter will automatically
attempt to negotiate TLSv1, and hopefully will succeed.

.. autoclass:: requests_toolbelt.adapters.ssl.SSLAdapter

.. _here: https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/

SourceAddressAdapter
--------------------

.. versionadded:: 0.3.0

The :class:`~requests_toolbelt.adapters.source.SourceAddressAdapter` allows a 
user to specify a source address for their connnection.

.. autoclass:: requests_toolbelt.adapters.source.SourceAddressAdapter

SocketOptionsAdapter
--------------------

.. versionadded:: 0.4.0

.. note::

    This adapter will only work with requests 2.4.0 or newer. The ability to
    set arbitrary socket options does not exist prior to requests 2.4.0.

The ``SocketOptionsAdapter`` allows a user to pass specific options to be set
on created sockets when constructing the Adapter without subclassing. The
adapter takes advantage of ``urllib3``'s `support`_ for setting arbitrary
socket options for each ``urllib3.connection.HTTPConnection`` (and
``HTTPSConnection``).

To pass socket options, you need to send a list of three-item tuples. For
example, ``requests`` and ``urllib3`` disable `Nagle's Algorithm`_ by default.
If you need to re-enable it, you would do the following:

.. code-block:: python

    import socket
    import requests
    from requests_toolbelt.adapters.socket_options import SocketOptionsAdapter

    nagles = [(socket.IPPROTO_TCP, socket.TCP_NODELAY, 0)]
    session = requests.Session()
    for scheme in session.adapters.keys():
        session.mount(scheme, SocketOptionsAdapter(socket_options=nagles))

This would re-enable Nagle's Algorithm for all ``http://`` and ``https://``
connections made with that session.

.. autoclass:: requests_toolbelt.adapters.socket_options.SocketOptionsAdapter

.. _support: https://urllib3.readthedocs.org/en/latest/pools.html?highlight=socket_options#urllib3.connection.HTTPConnection.socket_options
.. _Nagle's Algorithm: https://en.wikipedia.org/wiki/Nagle%27s_algorithm

TCPKeepAliveAdapter
-------------------

.. versionadded:: 0.4.0

.. note::

    This adapter will only work with requests 2.4.0 or newer. The ability to
    set arbitrary socket options does not exist prior to requests 2.4.0.

The ``TCPKeepAliveAdapter`` allows a user to pass specific keep-alive related
options as keyword parameters as well as arbitrary socket options.

.. note::

    Different keep-alive related socket options may not be available for your
    platform. Check the socket module for the availability of the following
    constants:

    - ``socket.TCP_KEEPIDLE``
    - ``socket.TCP_KEEPCNT``
    - ``socket.TCP_KEEPINTVL``

    The adapter will silently ignore any option passed for a non-existent
    option.

An example usage of the adapter:

.. code-block:: python

    import requests
    from requests_toolbelt.adapter.socket_options import TCPKeepAliveAdapter

    session = requests.Session()
    keep_alive = TCPKeepAliveAdapter(idle=120, count=20, interval=30)
    session.mount('https://region-a.geo-1.compute.hpcloudsvc.com', keep_alive)
    session.post('https://region-a.geo-1.compute.hpcloudsvc.com/v2/1234abcdef/servers',
                 # ...
                 )

In this case we know that creating a server on HP Public Cloud can cause
requests to hang without using TCP Keep-Alive. So we mount the adapter
specifically for that domain, instead of adding it to every ``https://`` and
``http://`` request.

.. autoclass:: requests_toolbelt.adapters.socket_options.TCPKeepAliveAdapter

