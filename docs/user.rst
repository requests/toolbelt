.. _user:

User Guide
==========

The ``requests-toolbelt`` contains a number of unrelated tools and utilities
for helping with use-cases that are not directly supported by the core
``requests`` library. This section of the documentation contains descriptions
of the various utilities included in the toolbelt, and how to use them.

Uploading Data
--------------

Streaming Multipart Data Encoder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requests has `support for multipart uploads`_, but the API means that using
that functionality to build exactly the Multipart upload you want can be
difficult or impossible. Additionally, when using Requests' Multipart upload
functionality all the data must be read into memory before being sent to the
server. In extreme cases, this can make it impossible to send a file as part of
a ``multipart/form-data`` upload.

The toolbelt contains a class that allows you to build multipart request bodies
in exactly the format you need, and to avoid reading files into memory. An
example of how to use it is like this:

::

    from requests_toolbelt import MultipartEncoder
    import requests

    with open('file.py', 'rb') as f:
        m = MultipartEncoder(
            fields={'field0': 'value', 'field1': 'value',
                    'field2': ('filename', f, 'text/plain')}
            )

        r = requests.post('http://httpbin.org/post', data=m,
                          headers={'Content-Type': m.content_type})

The ``MultipartEncoder`` has the ``.to_string()`` convenience method, as well.
This method renders the multipart body into a string. This is useful when
developing your code, allowing you to confirm that the multipart body has the
form you expect before you send it on.

The ``toolbelt`` also provides a way to monitor your streaming uploads with
the ``MultipartEncoderMonitor``.

.. _support for multipart uploads: http://docs.python-requests.org/en/latest/user/quickstart/#post-a-multipart-encoded-file

Monitoring Your Streaming Multipart Upload
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to stream your ``multipart/form-data`` upload then you're probably
in the situation where it might take a while to upload the content. In these
cases, it might make sense to be able to monitor the progress of the upload.
For this reason, the toolbelt provides the ``MultipartEncoderMonitor``. The
monitor wraps an instance of a ``MultipartEncoder`` and is used exactly like
the encoder. It provides a similar API with some additions:

- The monitor accepts a function as a callback. The function is called every
  time ``requests`` calls ``read`` on the monitor and passes in the monitor as
  an argument.

- The monitor tracks how many bytes have been read in the course of the
  upload.

You might use the monitor to create a progress bar for the upload. Here is `an
example using clint`_ which displays the progress bar.

To use the monitor you would follow a pattern like this::

    from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
    import requests

    def my_callback(monitor):
        # Your callback function
        pass

    e = MultipartEncoder(
        fields={'field0': 'value', 'field1': 'value',
                'field2': ('filename', open('file.py', 'rb'), 'text/plain')}
        )
    m = MultipartEncoderMonitor(e, my_callback)

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})

If you have a very simple use case you can also do::

    from requests_toolbelt import MultipartEncoderMonitor
    import requests

    def my_callback(monitor):
        # Your callback function
        pass

    m = MultipartEncoderMonitor.from_fields(
        fields={'field0': 'value', 'field1': 'value',
                'field2': ('filename', open('file.py', 'rb'), 'text/plain')},
        callback=my_callback
        )

    r = requests.post('http://httpbin.org/post', data=m,
                      headers={'Content-Type': m.content_type})


.. _example using clint: https://gitlab.com/sigmavirus24/toolbelt/blob/master/examples/monitor/progress_bar.py

Streaming Data from a Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are cases where you, the user, have a generator of some large quantity
of data and you already know the size of that data. If you pass the generator
to ``requests`` via the ``data`` parameter, ``requests`` will assume that you
want to upload the data in chunks and set a ``Transfer-Encoding`` header value
of ``chunked``. Often times, this causes the server to behave poorly. If you
want to avoid this, you can use the ``StreamingIterator``. You pass it the
size of the data and the generator.

.. code-block:: python

    from requests_toolbelt import StreamingIterator

    generator = some_function()  # Create your generator
    size = some_function_size()  # Get your generator's size
    content_type = content_type()  # Get the content-type of the data

    streamer = StreamingIterator(size, generator)
    r = requests.post('https://httpbin.org/post', data=streamer,
                      headers={'Content-Type': content_type})

The streamer will handle your generator for you and buffer the data before
passing it to ``requests``.

User-Agent Constructor
----------------------

Having well-formed user-agent strings is important for the proper functioning
of the web. Make server administators happy by generating yourself a nice
user-agent string, just like Requests does! The output of the user-agent
generator looks like this::

    >>> import requests_toolbelt
    >>> requests_toolbelt.user_agent('mypackage', '0.0.1')
    'mypackage/0.0.1 CPython/2.7.5 Darwin/13.0.0'

The Python type and version, and the platform type and version, will accurately
reflect the system that your program is running on. You can drop this easily
into your program like this::

    from requests_toolbelt import user_agent
    from requests import Session

    s = Session()
    s.headers = {
        'User-Agent': user_agent('my_package', '0.0.1')
        }

    r = s.get('https://api.github.com/users')

This will override the default Requests user-agent string for all of your HTTP
requests, replacing it with your own.

.. _adapters:

Adapters
--------

SSLAdapter
~~~~~~~~~~

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

    from requests_toolbelt import SSLAdapter

    import requests
    import ssl

    s = requests.Session()
    s.mount('https://github.com/', SSLAdapter(ssl.PROTOCOL_TLSv1))

Any future requests to GitHub made through that adapter will automatically
attempt to negotiate TLSv1, and hopefully will succeed.

.. _here: https://lukasa.co.uk/2013/01/Choosing_SSL_Version_In_Requests/

.. _authentication:

SocketOptionsAdapter
~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~

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

Authentication
--------------

GuessAuth
~~~~~~~~~

The ``GuessAuth`` auth type automatically detects whether to use basic auth or
digest auth::

    from requests_toolbelt import GuessAuth

    import requests

    requests.get('http://httpbin.org/basic-auth/user/passwd',
                 auth=GuessAuth('user', 'passwd'))
    requests.get('http://httpbin.org/digest-auth/auth/user/passwd',
                 auth=GuessAuth('user', 'passwd'))

This requires an additional request in case of basic auth, as usually basic
auth is sent preemptively.


HTTPProxyDigestAuth
-------------------

The ``HTTPProxyDigestAuth`` use digest authentication between the client and
the proxy.

    import requests
    from requests_toolbelt.auth import HTTPProxyDigestAuth


    proxies = {
            "http": "http://PROXYSERVER:PROXYPORT",
            "https": "https://PROXYSERVER:PROXYPORT",
            }
    url = "http://toolbelt.rtfd.org/"
    auth = HTTPProxyDigestAuth("USERNAME", "PASSWORD")
    requests.get(url, proxies=proxies, auth=auth)

Program would raise error if the username or password is rejected by the proxy.
